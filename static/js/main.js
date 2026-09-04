/* =========================================================
   SKILLMATCH - MAIN JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       1. MOBILE MENU
    ===================================================== */

    const menuButton = document.querySelector(".mobile-menu-btn");
    const navLinks = document.querySelector(".nav-links");

    if (menuButton && navLinks) {

        menuButton.addEventListener("click", function () {

            navLinks.classList.toggle("mobile-open");

        });

    }


    /* =====================================================
       2. PASSWORD SHOW / HIDE
    ===================================================== */

    const passwordToggles =
        document.querySelectorAll(".password-toggle");

    passwordToggles.forEach(function (button) {

        button.addEventListener("click", function () {

            const wrapper = button.closest(".password-wrapper");

            if (!wrapper) return;

            const input = wrapper.querySelector("input");

            if (!input) return;

            if (input.type === "password") {

                input.type = "text";

                button.textContent = "🙈";

            } else {

                input.type = "password";

                button.textContent = "👁";

            }

        });

    });


    /* =====================================================
       3. PASSWORD CONFIRMATION
    ===================================================== */

    const registerForm =
        document.querySelector("#registerForm");

    if (registerForm) {

        registerForm.addEventListener("submit", function (event) {

            const password =
                document.querySelector("#password");

            const confirmPassword =
                document.querySelector("#confirm_password");

            if (
                password &&
                confirmPassword &&
                password.value !== confirmPassword.value
            ) {

                event.preventDefault();

                alert("Passwords do not match.");

                confirmPassword.focus();

            }

        });

    }


    /* =====================================================
       4. PASSWORD STRENGTH
    ===================================================== */

    const passwordInput =
        document.querySelector("#password");

    const strengthText =
        document.querySelector("#passwordStrength");

    if (passwordInput && strengthText) {

        passwordInput.addEventListener("input", function () {

            const password = passwordInput.value;

            let strength = "";
            let score = 0;

            if (password.length >= 8) {
                score++;
            }

            if (/[A-Z]/.test(password)) {
                score++;
            }

            if (/[0-9]/.test(password)) {
                score++;
            }

            if (/[^A-Za-z0-9]/.test(password)) {
                score++;
            }


            if (password.length === 0) {

                strength = "";

            } else if (score <= 1) {

                strength = "Weak password";

            } else if (score === 2) {

                strength = "Medium password";

            } else {

                strength = "Strong password";

            }

            strengthText.textContent = strength;

        });

    }


    /* =====================================================
       5. RESUME FILE UPLOAD
    ===================================================== */

    const resumeInput =
        document.querySelector("#resume");

    const fileName =
        document.querySelector("#fileName");

    const uploadArea =
        document.querySelector(".resume-upload");

    if (resumeInput) {

        resumeInput.addEventListener("change", function () {

            if (!resumeInput.files.length) {
                return;
            }

            const file = resumeInput.files[0];

            const maxSize =
                10 * 1024 * 1024;

            const allowedTypes = [
                "application/pdf",

                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

                "application/msword"
            ];


            if (!allowedTypes.includes(file.type)) {

                alert(
                    "Please upload a PDF or Word document."
                );

                resumeInput.value = "";

                return;
            }


            if (file.size > maxSize) {

                alert(
                    "File size must be less than 10 MB."
                );

                resumeInput.value = "";

                return;
            }


            if (fileName) {

                fileName.textContent =
                    "Selected: " + file.name;

            }

            if (uploadArea) {

                uploadArea.classList.add("file-selected");

            }

        });

    }


    /* =====================================================
       6. DRAG & DROP RESUME
    ===================================================== */

    if (uploadArea && resumeInput) {

        uploadArea.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();

                uploadArea.classList.add("dragging");

            }
        );


        uploadArea.addEventListener(
            "dragleave",
            function () {

                uploadArea.classList.remove("dragging");

            }
        );


        uploadArea.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();

                uploadArea.classList.remove("dragging");

                const files =
                    event.dataTransfer.files;

                if (!files.length) {
                    return;
                }

                resumeInput.files = files;

                resumeInput.dispatchEvent(
                    new Event("change")
                );

            }
        );

    }


    /* =====================================================
       7. MATCH FILTERS
    ===================================================== */

    const filterButtons =
        document.querySelectorAll(".filter-btn");

    const matchCards =
        document.querySelectorAll(".match-card");


    filterButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            filterButtons.forEach(function (btn) {

                btn.classList.remove("active");

            });

            button.classList.add("active");


            const filter =
                button.dataset.filter || "all";


            matchCards.forEach(function (card) {

                const type =
                    card.dataset.type || "";

                if (
                    filter === "all" ||
                    type === filter
                ) {

                    card.style.display = "";

                } else {

                    card.style.display = "none";

                }

            });

        });

    });


    /* =====================================================
       8. MATCH SORTING
    ===================================================== */

    const sortSelect =
        document.querySelector("#sortMatches");

    const matchContainer =
        document.querySelector(".matches-grid");


    if (sortSelect && matchContainer) {

        sortSelect.addEventListener(
            "change",
            function () {

                const cards =
                    Array.from(
                        matchContainer.querySelectorAll(
                            ".match-card"
                        )
                    );

                const sortValue =
                    sortSelect.value;


                cards.sort(function (a, b) {

                    if (sortValue === "score") {

                        const scoreA =
                            parseFloat(
                                a.dataset.score || 0
                            );

                        const scoreB =
                            parseFloat(
                                b.dataset.score || 0
                            );

                        return scoreB - scoreA;

                    }


                    if (sortValue === "title") {

                        const titleA =
                            (
                                a.dataset.title || ""
                            ).toLowerCase();

                        const titleB =
                            (
                                b.dataset.title || ""
                            ).toLowerCase();

                        return titleA.localeCompare(
                            titleB
                        );

                    }


                    return 0;

                });


                cards.forEach(function (card) {

                    matchContainer.appendChild(card);

                });

            }
        );

    }


    /* =====================================================
       9. SEARCH
    ===================================================== */

    const searchInput =
        document.querySelector("#searchInput");

    const searchableCards =
        document.querySelectorAll(
            ".match-card, .opportunity-card"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const query =
                    searchInput.value
                        .toLowerCase()
                        .trim();


                searchableCards.forEach(function (card) {

                    const text =
                        card.textContent.toLowerCase();


                    if (text.includes(query)) {

                        card.style.display = "";

                    } else {

                        card.style.display = "none";

                    }

                });

            }
        );

    }


    /* =====================================================
       10. SMOOTH SCROLL
    ===================================================== */

    const smoothLinks =
        document.querySelectorAll(
            'a[href^="#"]'
        );


    smoothLinks.forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId =
                link.getAttribute("href");

            if (
                !targetId ||
                targetId === "#"
            ) {
                return;
            }

            const target =
                document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });


    /* =====================================================
       11. FADE-IN ANIMATION
    ===================================================== */

    const animatedElements =
        document.querySelectorAll(
            ".feature-card, .match-card, .dashboard-card, .stat-card"
        );


    animatedElements.forEach(function (element, index) {

        element.style.opacity = "0";

        element.style.transform =
            "translateY(10px)";


        setTimeout(function () {

            element.style.transition =
                "opacity .4s ease, transform .4s ease";

            element.style.opacity = "1";

            element.style.transform =
                "translateY(0)";

        }, index * 60);

    });


    /* =====================================================
       12. DELETE / DANGEROUS ACTION CONFIRMATION
    ===================================================== */

    const confirmButtons =
        document.querySelectorAll(
            "[data-confirm]"
        );


    confirmButtons.forEach(function (button) {

        button.addEventListener("click", function (event) {

            const message =
                button.dataset.confirm ||
                "Are you sure?";


            if (!confirm(message)) {

                event.preventDefault();

            }

        });

    });


    /* =====================================================
       13. APPLY BUTTON
    ===================================================== */

    const applyButtons =
        document.querySelectorAll(
            ".apply-button"
        );


    applyButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const originalText =
                button.textContent;

            button.disabled = true;

            button.textContent =
                "Applying...";


            setTimeout(function () {

                button.disabled = false;

                button.textContent =
                    originalText;

            }, 1500);

        });

    });


    /* =====================================================
       14. PROFILE SKILL INPUT
    ===================================================== */

    const skillInput =
        document.querySelector("#skillInput");

    const skillContainer =
        document.querySelector("#skillContainer");

    const addSkillButton =
        document.querySelector("#addSkill");


    if (
        skillInput &&
        skillContainer &&
        addSkillButton
    ) {

        addSkillButton.addEventListener(
            "click",
            function () {

                const skill =
                    skillInput.value.trim();


                if (!skill) {
                    return;
                }


                const tag =
                    document.createElement("span");

                tag.className = "skill-tag";

                tag.innerHTML =
                    skill +
                    ' <button type="button" class="remove-tag">×</button>';


                skillContainer.appendChild(tag);

                skillInput.value = "";

            }
        );


        skillContainer.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.classList.contains(
                        "remove-tag"
                    )
                ) {

                    event.target.parentElement.remove();

                }

            }
        );

    }


    /* =====================================================
       15. INTEREST INPUT
    ===================================================== */

    const interestInput =
        document.querySelector("#interestInput");

    const interestContainer =
        document.querySelector("#interestContainer");

    const addInterestButton =
        document.querySelector("#addInterest");


    if (
        interestInput &&
        interestContainer &&
        addInterestButton
    ) {

        addInterestButton.addEventListener(
            "click",
            function () {

                const interest =
                    interestInput.value.trim();


                if (!interest) {
                    return;
                }


                const tag =
                    document.createElement("span");

                tag.className =
                    "interest-tag";

                tag.innerHTML =
                    interest +
                    ' <button type="button" class="remove-tag">×</button>';


                interestContainer.appendChild(tag);

                interestInput.value = "";

            }
        );


        interestContainer.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.classList.contains(
                        "remove-tag"
                    )
                ) {

                    event.target.parentElement.remove();

                }

            }
        );

    }


    /* =====================================================
       16. ADMIN OPPORTUNITY FORM
    ===================================================== */

    const opportunityType =
        document.querySelector("#type");

    const companyInput =
        document.querySelector("#company");


    if (
        opportunityType &&
        companyInput
    ) {

        opportunityType.addEventListener(
            "change",
            function () {

                if (
                    opportunityType.value ===
                    "project"
                ) {

                    companyInput.placeholder =
                        "Project Owner / Organization";

                } else {

                    companyInput.placeholder =
                        "Company name";

                }

            }
        );

    }


    /* =====================================================
       17. DEADLINE VALIDATION
    ===================================================== */

    const deadline =
        document.querySelector("#deadline");


    if (deadline) {

        const today =
            new Date().toISOString().split("T")[0];

        deadline.min = today;

    }


    /* =====================================================
       18. PROFILE COMPLETION
    ===================================================== */

    const completionBar =
        document.querySelector(
            "#profileCompletion"
        );

    if (completionBar) {

        const percentage =
            parseInt(
                completionBar.dataset.value || 0
            );


        setTimeout(function () {

            completionBar.style.width =
                Math.min(
                    Math.max(percentage, 0),
                    100
                ) + "%";

        }, 300);

    }


    /* =====================================================
       19. AI SCREENING LOADING EFFECT
    ===================================================== */

    const screeningButton =
        document.querySelector(
            "#screenResume"
        );

    const screeningResult =
        document.querySelector(
            "#screeningResult"
        );


    if (
        screeningButton &&
        screeningResult
    ) {

        screeningButton.addEventListener(
            "click",
            function () {

                screeningButton.disabled = true;

                screeningButton.textContent =
                    "🤖 Analyzing Resume...";

                screeningResult.innerHTML =
                    "<p>AI Resume Screening in progress...</p>";

                setTimeout(function () {

                    screeningButton.disabled =
                        false;

                    screeningButton.textContent =
                        "🤖 Screen Resume";

                    screeningResult.innerHTML =
                        `
                        <div class="screening-success">
                            <strong>✓ Resume Analysis Complete</strong>
                            <p>
                                Your resume has been analyzed
                                successfully.
                            </p>
                        </div>
                        `;

                }, 1800);

            }
        );

    }


    /* =====================================================
       20. AI MATCHING BUTTON
    ===================================================== */

    const matchButton =
        document.querySelector(
            "#findMatches"
        );


    if (matchButton) {

        matchButton.addEventListener(
            "click",
            function () {

                const originalText =
                    matchButton.innerHTML;

                matchButton.disabled = true;

                matchButton.innerHTML =
                    "🤖 Finding Matches...";


                setTimeout(function () {

                    matchButton.disabled =
                        false;

                    matchButton.innerHTML =
                        originalText;

                    window.location.href =
                        "/matches";

                }, 1200);

            }
        );

    }


    /* =====================================================
       21. OPPORTUNITY TYPE FILTER
    ===================================================== */

    const typeFilter =
        document.querySelector(
            "#typeFilter"
        );


    if (typeFilter) {

        typeFilter.addEventListener(
            "change",
            function () {

                const selected =
                    typeFilter.value;

                const cards =
                    document.querySelectorAll(
                        ".match-card"
                    );


                cards.forEach(function (card) {

                    const cardType =
                        card.dataset.type || "";


                    if (
                        selected === "all" ||
                        selected === cardType
                    ) {

                        card.style.display = "";

                    } else {

                        card.style.display = "none";

                    }

                });

            }
        );

    }


    /* =====================================================
       22. AUTO-HIDE FLASH MESSAGE
    ===================================================== */

    const flashMessages =
        document.querySelectorAll(
            ".flash-message, .flash"
        );


    flashMessages.forEach(function (message) {

        setTimeout(function () {

            message.style.transition =
                "opacity .5s ease";

            message.style.opacity = "0";


            setTimeout(function () {

                message.remove();

            }, 500);

        }, 5000);

    });


    /* =====================================================
       23. CURRENT YEAR
    ===================================================== */

    const yearElements =
        document.querySelectorAll(
            ".current-year"
        );


    yearElements.forEach(function (element) {

        element.textContent =
            new Date().getFullYear();

    });


    /* =====================================================
       24. CONSOLE MESSAGE
    ===================================================== */

    console.log(
        "SkillMatch website loaded successfully 🚀"
    );

});