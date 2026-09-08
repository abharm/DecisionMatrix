# Updating the application

The editable source code is in `src\app`, not in `DM Application\DecisionMatrix.exe`.

1. Make code changes under `src\app`.
2. Close Decision Matrix if it is open.
3. From the `law_school_matrix` folder, run:

   ```powershell
   .\tools\build_and_deploy.ps1
   ```

4. Start the refreshed `DecisionMatrix.exe` from your desktop's `DM Application` folder.

The script creates a new executable and replaces the deployed one. It also refreshes `DecisionMatrix-Windows.zip` if you want to send the new version to someone else.
