Feature: User 1 attempts to buy a basegood
    Scenario: You have enough money
        Given The system is set up properly
        Then I buy the basegoods 1
        Then I should get a 200 response
        And my inventory should contain basegood 1

     Scenario: You dont have enough money
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I spend all my money
        Then I buy the basegoods 1
        Then I should get a 200 response
        And my inventory should not contain basegood 1
