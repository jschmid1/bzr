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
        Then I should get a 409 response
        And my inventory should not contain basegood 1

      Scenario: The resource on the map has been depleted
        Given The system is set up properly
        Then I make sure that the inventory is empty
        Then I make sure that the basegood 1 is not present on the map
        Then I make sure that I have enough money
        Then I buy the basegoods 1
        Then I expect "Resources exceeded on this map" in the message 
        Then I should get a 409 response
        And my inventory should not contain basegood 1
