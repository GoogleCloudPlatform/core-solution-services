# GENIE React app version 2

## Deploy to firebase

You must have `.env.production` in your webapp directory, with the firebase config for the app.

Make a copy of webapp/config.env and update with your firebase config.

Then to deploy:

```
$ npm run build
$ firebase deploy --only hosting:new-genie-ui
```
