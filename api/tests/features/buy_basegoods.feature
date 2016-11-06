Feature: User 1 attempts to buy a basegood

Scenario: You have enough money
Given some 'basegoods' are in the system
When I buy the 'basegoods' '1'
Then I should get a '200' response
And my inventory should contain 'basegood' '1'
