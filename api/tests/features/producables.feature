Feature: Query for all 'producables'
Scenario: Retrieve all items
Given some 'producables' are in the system
When I retrieve all 'producables'
Then I should get a '200' response
And I should get a list of 'producables'
