Feature: Select Menu choices from module 4
  Scenario: Remove a color without clearing other fields (TC-SM-13)
    Given the Select Menu page is open
    When I select Green and Blue and choose Mrs.
    And I remove Blue
    Then only Green remains and Mrs. is preserved

  Scenario: Unmatched search preserves selection (TC-SM-09)
    Given the Select Menu page is open
    And Green is selected
    When I search for an unavailable color
    Then no options are offered and Green remains
