# GENIE React app version 2

## Frontend Deployment to Firebase

This section outlines the commands used to build and deploy the frontend application to Firebase Hosting.

**Prerequisites:**

* **Firebase CLI Installed:** Ensure you have the Firebase Command Line Interface (CLI) installed. You can install it using your package manager (e.g., npm for Node.js projects).
* **Firebase Project Set Up:** You should have a Firebase project created in the Firebase Console.

**Deployment Steps:**

## Deploy to firebase

You must have `.env.production` in your webapp directory, with the firebase config for the app.

Make a copy of webapp/config.env and update with your firebase config.

1.  **Build the Application:** Before deploying, you need to build the production-ready version of your frontend application. Navigate to your project's web application directory and run the appropriate build command for your framework (e.g., `npm run build`). This command will generate the static assets for deployment, typically in a `dist` or `build` directory.

    ```bash
    cd <your_webapp_directory>
    <your_build_command>
    ```
    $ npm run build

2.  **Log in to Firebase (if not already):** If you haven't logged into the Firebase CLI recently, you might need to authenticate:

    ```bash
    firebase login
    ```

    Follow the prompts in your browser to log in with your Google account.

3.  **Set the Active Firebase Project:** Ensure the Firebase CLI is currently using the correct Firebase project. You can check the active project with:

    ```bash
    firebase use
    ```

    To switch to a different project or add a new one:

    ```bash
    firebase use <your_firebase_project_id_or_alias>
    firebase use --add
    ```

4.  **Apply a Hosting Target (Optional, for named deployments):** Firebase Hosting targets allow you to deploy to specific named sites within your project. If you want to use a specific target, you need to apply it:

    ```bash
    firebase target:apply hosting <your_hosting_target_name> <your_firebase_hosting_site_id>
    ```

    Replace `<your_hosting_target_name>` with the name you want to use for the target. 
    Replace `<your_firebase_hosting_site_id>` with the ID of your Firebase Hosting site (found in the Firebase Console). You only need to run this once per target name.

5.  **Deploy to Firebase Hosting:** Once the build is complete and the correct Firebase project and target (if used) are set, you can deploy the built application to Firebase Hosting.

    * **Deploy to a specific Hosting target (if configured):**

        ```bash
        firebase deploy --only hosting:<your_hosting_target_name>
        ```

    The CLI will upload the contents of your build output directory (configured in `firebase.json`) and make them live on your Firebase Hosting URL.

By following these steps, you can deploy your frontend application to Firebase Hosting. Remember to adjust the commands and directory names based on your specific project setup.
