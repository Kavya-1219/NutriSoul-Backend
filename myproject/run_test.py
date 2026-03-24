import subprocess
try:
    result = subprocess.run(['py', 'verify_food_logging.py'], capture_output=True, text=True)
    print("STDOUT:")
    print("\n".join(result.stdout.splitlines()[-20:]))
    print("STDERR:")
    print("\n".join(result.stderr.splitlines()[-20:]))
except Exception as e:
    print(f"Error running subprocess: {e}")
