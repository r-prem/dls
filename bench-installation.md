To setup the repository locally follow the steps mentioned below:

1. Install bench and setup a frappe-bench directory by following the [Installation Steps](https://frappeframework.com/docs/user/en/installation).
1. Start the server by running bench start.
1. In a separate terminal window, create a new site by running bench new-site dls.test.
1. Fork the LMS app
1. Run bench get-app <url-of-your-form>.
1. Run bench --site dls.test install-app dls.
1. Map your site to localhost with the command ```bench --site dls.test add-to-hosts```
1. Now open the URL http://dls.test:8000/ in your browser, you should see the app running.
