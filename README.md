# Hospital Slot Search and Registration Automation
This project automates the process of searching for available slots and registering on a hospital's WeChat Mini Program. It is specifically designed to:
1. Search for a specific hospital branch, department, and doctor.
2. Continuously search if no slots are available until a slot becomes free.
3. Automatically register once a slot is found.

---

## Features
- **Automated Search**: Specify the hospital branch, department, and doctor you are interested in.
- **Continuous Monitoring**: The program continuously checks for available slots in real time.
- **Quick Registration**: Once an available slot is found, the program immediately registers it to ensure you secure the appointment.
- **Customizable Configuration**: Easily configure search parameters like branch, department, and doctor details.

---

## Prerequisites
1. **Appium**: Ensure Appium is installed on your system.
2. **Device or Emulator**: This code works only on Android devices or emulators
3. **Python**: Ensure Python is installed on your system.
4. **Browser Driver**: Download and set up a compatible browser driver (e.g., ChromeDriver for Google Chrome).
5. **WeChat Mini Program Access**: You need an active WeChat account with access to the hospital's mini program. Also make sure WeChat is in developer mode.

---

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/anqi-guo/miniProgramBot
   cd miniProgramBot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage
1. Run Appium in terminal
   ```bash
   appium --allow-cors
   ```

2. Start an android emulator or connect an android phone to the computer

3. Configure the search parameters in the `.env` file:
   ```env
   {
       "BRANCH": "Main Campus",
       "DEPARTMENT": "Cardiology",
       "DOCTOR": "Dr. Zhang"
   }
   ```

4. Run the script:
   ```bash
   python main.py
   ```

5. The program will:
   - Open the hospital's WeChat Mini Program.
   - Navigate to the specified hospital branch, department, and doctor.
   - Continuously search for available slots.
   - Automatically register once a slot is found.

---

## Notes

- **Continuous Monitoring**: Ensure your system remains connected to the internet while the program is running.
- **WeChat Account**: Ensure your account is logged in and has the necessary permissions to access the mini program.
- **Legal Considerations**: Ensure the use of automation complies with the hospital's terms of service and WeChat Mini Program policies.

---

## Troubleshooting

- **Browser Not Opening**:
  Ensure the browser driver is correctly installed and matches your browser version.
- **No Slots Found**:
  Verify the search parameters in `.env` and ensure they match the hospital's data.
- **Unexpected Errors**:
  Check the console output for detailed error messages and debug as needed.

---

## Future Improvements

- Notification system (e.g., email or SMS) when a slot becomes available.
- Enhanced error handling and logging.
- Integration with other hospital appointment systems.
