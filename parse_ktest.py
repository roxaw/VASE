import os
import subprocess
import json

def parse_ktest_file(ktest_file):
    """Run ktest-tool and capture its output."""
    result = subprocess.run(['ktest-tool', ktest_file], capture_output=True, text=True)
    return result.stdout

def extract_variables(log_content):
    """Extract variable names and values from ktest-tool output."""
    variables = {}
    name = None  # To hold the current variable name
    lines = log_content.splitlines()
    
    for line in lines:
        # Check for variable name
        if "name:" in line:
            name = line.split(":")[-1].strip().strip("'")
        
        # Check for integer values
        elif "int :" in line and name:
            value = line.split(":")[-1].strip()
            if name not in variables:
                variables[name] = []
            variables[name].append(value)
            name = None  # Reset after processing
    
    return variables

def identify_limited_valued_variables(variables, threshold=5):
    """Identify variables with unique value counts below the threshold."""
    limited_valued_vars = {}
    for var, values in variables.items():
        unique_values = set(values)
        if len(unique_values) <= threshold:
            limited_valued_vars[var] = list(unique_values)
    return limited_valued_vars

def main():
    log_dir = 'klee-out-2'  # Change this to your actual log directory
    all_variables = {}

    # Walk through the directory and process .ktest files
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            if file.endswith('.ktest'):
                ktest_path = os.path.join(root, file)
                log_content = parse_ktest_file(ktest_path)
                variables = extract_variables(log_content)
                
                # Aggregate variables across all files
                for var, values in variables.items():
                    if var not in all_variables:
                        all_variables[var] = []
                    all_variables[var].extend(values)

    # Identify limited-valued variables
    limited_valued_variables = identify_limited_valued_variables(all_variables)
    print(json.dumps(limited_valued_variables, indent=4))

if __name__ == '__main__':
    main()
