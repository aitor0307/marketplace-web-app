-- Separate database for the test suite, which drops every table after each
-- test (see app/config/testing.py). Runs only when the volume is first created.
CREATE DATABASE marketplace_test OWNER marketplace;
