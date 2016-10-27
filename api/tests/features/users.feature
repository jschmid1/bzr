Feature: GET all users
Scenario: Query all users
Given Some 'users' are in the system
When I retrieve all 'users'
Then I should get a '200' response
And I should get a list of 'users'
