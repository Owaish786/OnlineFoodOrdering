import pytest
from app import calculate_fine

# Four parameterized test cases for valid overdue days
@pytest.mark.parametrize("overdue_days, expected_fine", [
    (0, 0),       # Test case 1: 0 days overdue = $0
    (1, 5),       # Test case 2: 1 day overdue = $5
    (3, 15),      # Test case 3: 3 days overdue = $15
    (10, 50),     # Test case 4: 10 days overdue = $50
])
def test_calculate_fine_valid(overdue_days, expected_fine):
    assert calculate_fine(overdue_days) == expected_fine

# Test case for negative overdue days (asserts ValueError)
def test_calculate_fine_negative_days():
    with pytest.raises(ValueError, match="Overdue days cannot be negative"):
        calculate_fine(-1)

