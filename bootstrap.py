# bootstrap.py
import subprocess
import sys
import logging
import os # Import os for path operations

# Configure logging
# It's good practice to get a logger by name rather than using the root logger directly,
# especially if this script might become part of a larger application.
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_installed_packages():
    """
    Retrieves a dictionary of installed packages and their versions.
    Returns:
        dict: A dictionary where keys are package names and values are their versions.
              Returns an empty dict if an error occurs.
    """
    installed_pkgs = {}
    try:
        # pip freeze outputs 'package==version'
        # Using text=True for subprocess.check_output decodes output as string
        output = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze", "--disable-pip-version-check"],
            text=True,
            stderr=subprocess.PIPE # Capture stderr in case of warnings/errors
        )
        for line in output.splitlines():
            line = line.strip()
            if line and "==" in line:
                name, version = line.split("==", 1)
                installed_pkgs[name.strip()] = version.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to retrieve installed packages (pip freeze failed): {e.stderr.strip()}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting installed packages: {e}")
    return installed_pkgs

def get_required_packages(requirements_file='requirements.txt'):
    """
    Reads packages and their version specifiers from a requirements.txt file.
    Returns:
        list: A list of package specifiers (e.g., ['requests==2.28.1', 'Flask>=2.0']).
              Returns an empty list if the file is not found or an error occurs.
    """
    required_pkgs = []
    if not os.path.exists(requirements_file):
        logger.error(f"'{requirements_file}' not found. Please create it with your project dependencies.")
        return []

    try:
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'): # Ignore empty lines and comments
                    required_pkgs.append(line)
    except Exception as e:
        logger.error(f"Error reading '{requirements_file}': {e}")
    return required_pkgs

def install_package(package_specifier: str, retries: int = 3):
    """
    Attempts to install a single package with retries.
    Args:
        package_specifier (str): The package string (e.g., 'requests==2.28.1').
        retries (int): Number of times to retry installation on failure.
    Returns:
        bool: True if installation was successful, False otherwise.
    """
    logger.info(f"Attempting to install: {package_specifier}")
    for attempt in range(1, retries + 1):
        try:
            # Use check=True to raise CalledProcessError on non-zero exit code
            # Capture output for cleaner console and logging
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_specifier],
                check=True,
                capture_output=True,
                text=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            logger.info(f"Successfully installed {package_specifier}.")
            logger.debug(f"Pip install stdout for {package_specifier}:\n{result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"Installation of {package_specifier} failed (attempt {attempt}/{retries}). "
                f"Error: {e.returncode} - {e.stderr.strip()}"
            )
            if attempt == retries:
                logger.error(f"Failed to install {package_specifier} after {retries} attempts.")
        except FileNotFoundError:
            logger.error(f"Python executable or pip command not found. Please ensure Python and pip are correctly installed and in your PATH.")
            return False # Critical error, no point in retrying
        except Exception as e:
            logger.error(f"An unexpected error occurred during installation of {package_specifier} (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                logger.error(f"Failed to install {package_specifier} after {retries} attempts.")
    return False

def validate_and_install_dependencies():
    """
    Main function to validate and install project dependencies.
    It now correctly checks for package versions based on requirements.txt.
    """
    required_packages_specs = get_required_packages()
    if not required_packages_specs:
        logger.info("No packages specified in requirements.txt or file not found. Skipping dependency check.")
        return

    logger.info(f"Required packages from requirements.txt: {required_packages_specs}")

    # Initial check of installed packages
    installed_packages_map = get_installed_packages()
    logger.info(f"Currently installed packages: {installed_packages_map}")

    # Identify missing or incorrectly versioned packages
    packages_to_install = []
    for specifier in required_packages_specs:
        # Attempt to parse package name and version from specifier
        # Simple split for 'package==version' or 'package'
        # More complex parsing needed for 'package>=version', '<', '~=', etc.
        # For full specifier parsing, a library like `packaging` would be ideal.
        # For simplicity, we'll assume exact matches or just base name checks here.
        package_name = specifier.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()

        if package_name not in installed_packages_map:
            logger.info(f"'{package_name}' is not installed. Adding '{specifier}' to install list.")
            packages_to_install.append(specifier)
        elif '==' in specifier:
            # Check for exact version match
            required_version = specifier.split('==')[1].strip()
            if installed_packages_map.get(package_name) != required_version:
                logger.info(f"'{package_name}' installed version ({installed_packages_map.get(package_name)}) "
                            f"does not match required version ({required_version}). Adding '{specifier}' to install list.")
                packages_to_install.append(specifier)
        # For other specifiers (>=, <, etc.), pip install -r is more reliable.
        # This individual check only handles '==' accurately, otherwise it's a base name check.


    if not packages_to_install:
        logger.info("All required packages are already installed and at the correct versions.")
        return True

    logger.warning(f"The following packages need to be installed/updated: {packages_to_install}")
    all_installed_successfully = True
    for package_spec in packages_to_install:
        if not install_package(package_spec):
            all_installed_successfully = False
            # Continue trying to install others, or break if you want to fail fast
            # For now, we'll continue to try other packages
            # break # Uncomment this line if you want to stop on the first failure

    if not all_installed_successfully:
        logger.error("Some packages failed to install. Please check the logs above for details.")
        return False

    # Final validation after installation attempts
    final_installed_packages_map = get_installed_packages()
    missing_after_attempts = []
    for specifier in required_packages_specs:
        package_name = specifier.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
        if package_name not in final_installed_packages_map:
            missing_after_attempts.append(specifier)
        elif '==' in specifier:
            required_version = specifier.split('==')[1].strip()
            if final_installed_packages_map.get(package_name) != required_version:
                missing_after_attempts.append(specifier)

    if missing_after_attempts:
        logger.critical(
            f"CRITICAL: The following required packages are still missing or incorrect after all installation attempts: {missing_after_attempts}"
        )
        return False
    else:
        logger.info("All required packages are now successfully installed and validated.")
        return True


if __name__ == "__main__":
    success = validate_and_install_dependencies()
    if not success:
        logger.critical("Dependency validation and installation failed. Exiting.")
        sys.exit(1) # Exit with a non-zero code to indicate failure
    else:
        logger.info("Dependency validation and installation completed successfully.")