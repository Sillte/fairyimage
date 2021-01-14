"""Version's attribute test.
"""

import pytest
import fairyimage  

def test_version(): 
    assert hasattr(fairyimage, "__version__" )


if __name__ == "__main__":
    pytest.main(["--capture=no"])
