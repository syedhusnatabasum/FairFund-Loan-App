document.addEventListener("DOMContentLoaded", function () {

    console.log("FairApp loaded successfully.");

    const passwordInput =
        document.getElementById("password");

    const strengthBar =
        document.getElementById("strength-bar");

    const passwordMessage =
        document.getElementById("password-message");


    if (passwordInput) {

        passwordInput.addEventListener(
            "input",
            function () {

                const password =
                    passwordInput.value;

                if (password.length === 0) {

                    strengthBar.style.width = "0%";

                    passwordMessage.innerText =
                        "Password must contain at least 8 characters.";

                }

                else if (password.length < 8) {

                    strengthBar.style.width = "30%";

                    passwordMessage.innerText =
                        "❌ Too short - minimum 8 characters.";

                }

                else if (password.length < 10) {

                    strengthBar.style.width = "60%";

                    passwordMessage.innerText =
                        "⚠️ Good - you can make it stronger.";

                }

                else {

                    strengthBar.style.width = "100%";

                    passwordMessage.innerText =
                        "✅ Strong password.";

                }

            }
        );

    }

});


function togglePassword() {

    const password =
        document.getElementById("password");

    const button =
        document.querySelector(".show-password");


    if (password.type === "password") {

        password.type = "text";

        button.innerText = "🙈";

    }

    else {

        password.type = "password";

        button.innerText = "👁";

    }

}