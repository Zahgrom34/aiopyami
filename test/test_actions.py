from aiopyami.formats import Action
from unittest import TestCase, main as unittest_main


class TestActions(TestCase):
    def test_action_convertion(self):
        first_value = Action("Login", {
            "Username": "test",
            "Secret": "test"
        }).ami_format()
        
        second_value = "Action: Login\r\nUsername: test\r\nSecret: test\r\n\r\n"

        self.assertEqual(first_value, second_value, msg=first_value)


if __name__ == "__main__":
    unittest_main()