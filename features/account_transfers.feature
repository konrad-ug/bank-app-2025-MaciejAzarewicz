Feature: Account transfers

Scenario: User can make incoming transfer
    Given Account registry is empty
    When I create an account using name: "jan", last name: "kowalski", pesel: "90050512345"
    And I make incoming transfer of "100" to account with pesel: "90050512345"
    Then Account with pesel "90050512345" has balance equal to "100"

Scenario: User can make outgoing transfer
    Given Account registry is empty
    When I create an account using name: "jan", last name: "kowalski", pesel: "90050512345"
    And I make incoming transfer of "500" to account with pesel: "90050512345"
    And I make outgoing transfer of "200" from account with pesel: "90050512345"
    Then Account with pesel "90050512345" has balance equal to "300"

Scenario: User can make express transfer with fee
    Given Account registry is empty
    When I create an account using name: "jan", last name: "kowalski", pesel: "90050512345"
    And I make incoming transfer of "200" to account with pesel: "90050512345"
    And I make express transfer of "100" from account with pesel: "90050512345"
    Then Account with pesel "90050512345" has balance equal to "99"

Scenario: Cannot make transfer to non-existent account
    Given Account registry is empty
    When I make incoming transfer of "100" to account with pesel: "99999999999"
    Then Response status code should be "404"

Scenario: Cannot make transfer with invalid amount
    Given Account registry is empty
    When I create an account using name: "jan", last name: "kowalski", pesel: "90050512346"
    And I make incoming transfer of "-50" to account with pesel: "90050512346"
    Then Response status code should be "400"