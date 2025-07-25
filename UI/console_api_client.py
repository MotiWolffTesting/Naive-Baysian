import requests
import os

# Constants for API connection
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DECODE_ERROR_MSG = "Error: Could not decode server response. Raw response:"
TIMEOUT_SECONDS = 30

# Train the model via API (non-interactive if params provided)
def train_model(file_path=None, target_column=None):
    if file_path is None:
        file_path = input("Enter file path (csv): ")
    if target_column is None:
        target_column = input("Enter target column name: ")
    try:
        with open(file_path, "rb") as f:
            # Send POST request to /train endpoint
            response = requests.post(
                f"{API_URL}/train",
                files={"file": f},
                data={"target_column": target_column},
                timeout=TIMEOUT_SECONDS
            )
        try:
            result = response.json()
            if "status" in result:
                # Print message if model is already cached
                if result.get("cached"):
                    print("Model is already built for this dataset and target column.")
                else:
                    print("Model built successfully!")
                print(f"Target column: {result.get('target_column', 'N/A')}")
                return True
            else:
                print("Error:", result.get('error', 'Unknown error'))
                return False
        except Exception:
            print(f"{DECODE_ERROR_MSG} {response.text}")
            return False
    except FileNotFoundError:
        print("File not found, try again.")
        return False
    except Exception as e:
        print(f"Error loading file: {e}")
        return False

# Test model accuracy via API (non-interactive if params provided)
def test_model(file_path=None, target_column=None):
    if file_path is None:
        file_path = input("Enter a file path: ")
    try:
        with open(file_path, "rb") as f:
            # Read CSV to get columns if needed
            import pandas as pd
            df = pd.read_csv(file_path)
            if target_column is None:
                print("Available columns in test data:")
                for i, header in enumerate(df.columns):
                    print(f"{i+1}. {header}")
                target_column = input("Enter target column name for test data: ")
            if target_column not in df.columns:
                print("Target column not found in test data.")
                return
            # Reset file pointer and send POST request to /test
            f.seek(0)
            files = {"file": f}
            data = {}
            if target_column.strip():
                data["target_column"] = target_column
            response = requests.post(f"{API_URL}/test", files=files, data=data, timeout=TIMEOUT_SECONDS)
        try:
            result = response.json()
            if "accuracy" in result:
                print(f"Model Accuracy: {result['accuracy']:.2%}")
            else:
                print("Error:", result.get('error', 'Unknown error'))
        except Exception:
            print(f"{DECODE_ERROR_MSG} {response.text}")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"Error loading test file: {e}")

# Classify a single user-input record
def predict_single_record():
    # First get model info to know what features are needed
    response = requests.get(f"{API_URL}/info", timeout=TIMEOUT_SECONDS)
    try:
        model_info = response.json()
        if "Features" not in model_info:
            print("Model is not trained yet.")
            return
        
        features = model_info["Features"]
        print("Enter values for the following features:")
        
        # Collect feature values from user
        record = {}
        for feature in features:
            value = input(f"{feature}: ")
            record[feature] = value
            
        # Send prediction request
        response = requests.post(f"{API_URL}/predict", json=record, timeout=TIMEOUT_SECONDS)
        try:
            result = response.json()
            if "prediction" in result:
                print(f"Classification results: {result['prediction']}.")
            else:
                print("Error:", result.get('error', 'Unknown error'))
        except Exception:
            print(f"{DECODE_ERROR_MSG} {response.text}")
    except Exception:
        print("Error getting model information.")

# Display detailed model information
def show_model_info():
    response = requests.get(f"{API_URL}/info", timeout=TIMEOUT_SECONDS)
    try:
        info = response.json()
        print("\nModel Information")
        for key, value in info.items():
            if key == "Features":
                print(f"{key}: {', '.join(value)}")
            elif key == 'Classes':
                print(f"{key}: {', '.join(map(str, value))}")
            else:
                print(f"{key}: {value}")
    except Exception:
        print(f"{DECODE_ERROR_MSG} {response.text}")

def main():
    """Main application workflow"""
    print("=== Naive Bayes Classifier (API Client)")
    
    # Step 1: Load training data
    if not train_model():
        return
    
    # Step 2: Show main menu
    main_menu()

def main_menu():
    """Display and handle main menu options"""
    options = [
        "Check model accuracy with a data file",
        "Classify a single record",
        "Display info on model",
        "Exit"
    ]
    
    while True:
        print("\nChoose option:")
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        
        choice = input("Enter number: ")
        
        if choice == "1":
            test_model()
        elif choice == "2":
            predict_single_record()
        elif choice == "3":
            show_model_info()
        elif choice == "4":
            print("Thank you for using the classifier. Good Bye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()