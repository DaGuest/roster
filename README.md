# roster
A service that parses a roster-pdf and converts it to a calendar event format and adds it to a google calendar.

## Installing the service
1. Copy the `roster.service` file into `/etc/systemd/system` folder.

2. Change **DIRECTORY_OF_THE_PYTHON_SCRIPT** into the directory where the `service_runner.py` script is located.

3. Change **PATH_TO_THE_PYTHON_EXECUTABLE_SCRIPT** into the path where the python executable is located.
Use `python -c "import os; print(os.environ['_'])"` to find where that is.

4. Reload the systemctl unit to load our service into it's registry:
`systemctl daemon-reload`

5. Start the service:
`systemctl start roster.service`

To stop the service use:
`systemctl stop roster.service`