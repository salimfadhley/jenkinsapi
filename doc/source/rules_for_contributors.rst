Rules for Contributors
======================

The JenkinsAPI project welcomes contributions via GitHub. Please bear in mind the following guidelines when preparing your pull-request.

Python compatibility
--------------------

The project currently targets Python 2.7, and Python 3.4 to 3.6. Please do not add any features which
will break our Python 2.7 version or are not Python 2.7 *and* 3+ compatible. 

Test Driven Development
-----------------------

Please do not submit pull requests without tests. That's really important. Our project is all about test-driven development. It would be
embarrasing if our project failed because of a lack of tests!

You might want to follow a typical test driven development cycle: http://en.wikipedia.org/wiki/Test-driven_development

Put simply: Write your tests first and only implement features required to make your tests pass. Do not let your implementation get ahead of your tests.

Features implemented without tests will be removed. Unmaintained features (which break because of changes in Jenkins) will also be removed.

Check the CI status before comitting
------------------------------------

We have a Travis CI account - please verify that your branch works before making a pull request.

Any problems?
-------------

If you are stuck on something, please post to the issue tracker. Do not contact the developers directly.
