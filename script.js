document.addEventListener("DOMContentLoaded", function() {

    // 1. ПРОВЕРКА ФОРМЫ ОБРАТНОЙ СВЯЗИ (Контакты)
    let contactForm = document.getElementById("feedbackForm");
    if (contactForm) {
        contactForm.addEventListener("submit", function(event) {
            event.preventDefault();
            let name = document.getElementById("nameInput").value.trim();
            let email = document.getElementById("emailInput").value.trim();
            let message = document.getElementById("messageInput").value.trim();
            
            let nameError = document.getElementById("nameError");
            let emailError = document.getElementById("emailError");
            let messageError = document.getElementById("messageError");
            let successMessage = document.getElementById("successMessage");
            
            nameError.innerText = "";
            emailError.innerText = "";
            messageError.innerText = "";
            successMessage.innerText = "";
            
            let isValid = true;
            if (name.length < 2) { nameError.innerText = "Введите имя (минимум 2 буквы)"; isValid = false; }
            if (email === "") { emailError.innerText = "Введите Email"; isValid = false; } 
            else if (!email.includes("@") || !email.includes(".")) { emailError.innerText = "Некорректный Email"; isValid = false; }
            if (message === "") { messageError.innerText = "Напишите сообщение"; isValid = false; }
            
            if (isValid) {
                successMessage.innerText = "Сообщение успешно отправлено!";
                contactForm.reset();
            }
        });
    }

    // 2. ФИЛЬТРАЦИЯ И ЗАГРУЗКА КАТАЛОГА (Каталог)
    let filterForm = document.getElementById("filterForm");
    if (filterForm) {
        let routesList = document.getElementById("routesList");
        
        // Загружаем данные с сервера
        fetch("http://127.0.0.1:8000/api/routes")
            .then(response => response.json())
            .then(data => {
                routesList.innerHTML = ""; // Очищаем контейнер перед вставкой
                for (let i = 0; i < data.length; i++) {
                    let route = data[i];
                    let cardHTML = `
                        <article class="route-card card">
                            <div class="route-left">
                                <h3>${route.from_city} — ${route.to_city}</h3>
                                <p class="route-number">Номер поезда: ${route.train_number}</p>
                            </div>
                            <div class="route-center">
                                <p class="route-time">${route.dep_time} → ${route.arr_time}</p>
                                <p class="route-duration">(${route.duration} в пути)</p>
                            </div>
                            <div class="route-right">
                                <p class="price">от ${route.price} ₽</p>
                                <a href="item.html?id=${route.id}" class="btn">Выбрать</a>
                            </div>
                        </article>
                    `;
                    routesList.innerHTML += cardHTML;
                }
            })
            .catch(error => {
                console.error("Ошибка загрузки:", error);
                routesList.innerHTML = "<p style='color:red;'>Не удалось загрузить рейсы с сервера. Сервер включен?</p>";
            });

        // Логика фильтрации
        filterForm.addEventListener("submit", function(event) {
            event.preventDefault(); 
            let fromValue = document.getElementById("fromInput").value.toLowerCase().trim();
            let toValue = document.getElementById("toInput").value.toLowerCase().trim();
            let priceValue = document.getElementById("priceInput").value.replace(/[^0-9]/g, ""); 
            let filterError = document.getElementById("filterError");
            filterError.innerText = ""; 

            if (fromValue === "" && toValue === "" && priceValue === "") {
                filterError.innerText = "Введите хотя бы один параметр";
                return;
            }
            
            let routeCards = document.querySelectorAll(".route-card");
            for (let i = 0; i < routeCards.length; i++) {
                let card = routeCards[i];
                let title = card.querySelector(".route-left h3").innerText.toLowerCase();
                let priceText = card.querySelector(".price").innerText;
                let cardPrice = parseInt(priceText.replace(/[^0-9]/g, "")); 
                
                let parts = title.split("—");
                let cardFrom = parts[0].trim(); 
                let cardTo = parts[1].trim();   
                
                let isMatch = true; 
                if (fromValue !== "" && !cardFrom.includes(fromValue)) isMatch = false;
                if (toValue !== "" && !cardTo.includes(toValue)) isMatch = false;
                if (priceValue !== "" && cardPrice > parseInt(priceValue)) isMatch = false;

                card.style.display = isMatch ? "flex" : "none"; 
            }
        });
    }

    // 3. СТРАНИЦА РЕЙСА (item.html) + API ПОГОДЫ
    let itemRouteTitle = document.getElementById("itemRouteTitle");
    if (itemRouteTitle) {
        let urlParams = new URLSearchParams(window.location.search);
        let routeId = urlParams.get("id");

        if (routeId) {
            // Запрашиваем данные конкретного рейса по ID из базы
            fetch(`http://127.0.0.1:8000/api/routes/${routeId}`)
                .then(response => {
                    if (!response.ok) throw new Error("Рейс не найден");
                    return response.json();
                })
                .then(data => {
                    // Подставляем данные в HTML
                    itemRouteTitle.innerText = data.from_city + " — " + data.to_city;
                    document.getElementById("itemPriceText").innerText = data.price;
                    document.getElementById("itemTrain").innerText = data.train_number;
                    document.getElementById("itemDep").innerText = data.dep_time;
                    document.getElementById("itemArr").innerText = data.arr_time;
                    document.getElementById("itemDur").innerText = data.duration;

                    // Передаем данные в Заказ (ссылку)
                    let bookBtn = document.getElementById("bookBtn");
                    bookBtn.href = `order.html?id=${data.id}&from=${data.from_city}&to=${data.to_city}&price=${data.price}`;

                    // Погода
                    const cityCoordinates = {
                        "Санкт-Петербург": { lat: 59.93, lon: 30.31 },
                        "Москва": { lat: 55.75, lon: 37.61 },
                        "Казань": { lat: 55.79, lon: 49.10 },
                        "Сочи": { lat: 43.60, lon: 39.73 },
                        "Екатеринбург": { lat: 56.83, lon: 60.60 },
                        "Нижний Новгород": { lat: 56.32, lon: 44.00 }
                    };
                    
                    let coords = cityCoordinates[data.to_city] || cityCoordinates["Санкт-Петербург"];
                    let apiUrl = `https://api.open-meteo.com/v1/forecast?latitude=${coords.lat}&longitude=${coords.lon}&current_weather=true`;

                    fetch(apiUrl)
                        .then(res => res.json())
                        .then(weatherData => {
                            document.getElementById("weatherResult").innerHTML = `🌡 ${weatherData.current_weather.temperature}°C, ветер ${weatherData.current_weather.windspeed} м/с`;
                        })
                        .catch(() => {
                            document.getElementById("weatherResult").innerHTML = `<span style="color: red;">Не удалось загрузить погоду</span>`;
                        });
                })
                .catch(error => {
                    itemRouteTitle.innerText = "Рейс не найден";
                });
        }
    }

    // 4. СТРАНИЦА ЗАКАЗА (order.html)
    let seatsContainer = document.getElementById("seatsContainer");
    if (seatsContainer) {
        let urlParams = new URLSearchParams(window.location.search);
        let routeId = urlParams.get("id"); // Читаем ID рейса из ссылки
        let fromCity = urlParams.get("from");
        let toCity = urlParams.get("to");
        let ticketPrice = urlParams.get("price");
        let pricePerSeat = 2500; // по умолчанию

        if (fromCity && toCity) {
            document.getElementById("routeInfo").innerText = `${fromCity} — ${toCity} | Поезд 001А | 03 ноября | 10:00 → 14:00`;
        }
        if (ticketPrice) {
            pricePerSeat = parseInt(ticketPrice);
            document.getElementById("ticketPrice").innerText = pricePerSeat;
        }

        let allSeats = document.querySelectorAll(".seat");
        let selectedSeatsCount = 0;

        // Логика выбора мест
        for (let i = 0; i < allSeats.length; i++) {
            let seat = allSeats[i];
            if (seat.classList.contains("occupied")) continue;

            seat.addEventListener("click", function() {
                this.classList.toggle("selected");
                let selectedSeats = document.querySelectorAll(".seat.selected");
                selectedSeatsCount = selectedSeats.length;

                document.getElementById("selectedSeatsText").innerText = "Выбрано мест: " + selectedSeatsCount;
                let total = selectedSeatsCount * pricePerSeat;
                document.getElementById("totalPrice").innerText = "Итого: " + total + " ₽";
            });
        }

        // --- ИСПРАВЛЕННЫЙ БЛОК: Обработка кнопки "Оплатить" ---
        let btnPay = document.getElementById("btnPay");
        if (btnPay) {
            btnPay.addEventListener("click", async function() {
                let userId = localStorage.getItem("userId");
                
                if (!userId) {
                    alert("Пожалуйста, войдите в профиль, чтобы купить билет!");
                    window.location.href = "profile.html";
                    return;
                }

                if (!routeId) {
                    alert("Вы не выбрали рейс! Пожалуйста, вернитесь в каталог.");
                    window.location.href = "catalog.html";
                    return;
                }

                let selectedSeats = document.querySelectorAll(".seat.selected");
                if (selectedSeats.length === 0) {
                    alert("Выберите хотя бы одно место!");
                    return;
                }

                // Меняем текст на кнопке, чтобы показать загрузку
                btnPay.innerText = "Оплата...";
                btnPay.disabled = true;

                // Цикл, который покупает билеты ПО ОЧЕРЕДИ
                for (let i = 0; i < selectedSeats.length; i++) {
                    let seatNum = selectedSeats[i].innerText;
                    
                    try {
                        // await ждет ответа сервера, и только потом цикл идет дальше
                        let response = await fetch("http://127.0.0.1:8000/api/orders", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                user_id: parseInt(userId),
                                route_id: parseInt(routeId),
                                seat_number: parseInt(seatNum)
                            })
                        });
                        
                        if (!response.ok) {
                            console.error("Не удалось купить место " + seatNum);
                        }
                    } catch (error) {
                        console.error("Ошибка сети:", error);
                    }
                }

                // Когда все места куплены (цикл закончился), перекидываем в профиль
                alert("Билеты успешно куплены! Проверьте личный кабинет.");
                window.location.href = "profile.html";
            });
        }
    }

    // 5. СТРАНИЦА ПРОФИЛЯ (profile.html)
    let authSection = document.getElementById("authSection");
    if (authSection) {
        let isLoginMode = true;

        let loggedInUserId = localStorage.getItem("userId");
        let loggedInEmail = localStorage.getItem("userEmail");

        function showProfile() {
            authSection.style.display = "none";
            document.getElementById("profileSection").style.display = "block";
            document.getElementById("userEmailDisplay").innerText = loggedInEmail;
            
            fetch(`http://127.0.0.1:8000/api/orders/user/${loggedInUserId}`)
                .then(res => res.json())
                .then(orders => {
                    let list = document.getElementById("myOrdersList");
                    list.innerHTML = "";
                    if (orders.length === 0) {
                        list.innerHTML = "<p>У вас пока нет купленных билетов.</p>";
                    } else {
                        orders.forEach(order => {
                            list.innerHTML += `
                                <div style="border-bottom: 1px solid #ccc; padding: 10px 0;">
                                    <p><strong>Рейс:</strong> ${order.from_city} — ${order.to_city}</p>
                                    <p><strong>Поезд:</strong> ${order.train_number} | <strong>Место:</strong> ${order.seat_number}</p>
                                    <p><strong>Цена:</strong> ${order.price} ₽</p>
                                </div>
                            `;
                        });
                    }
                });
        }

        if (loggedInUserId) {
            showProfile();
        } else {
            authSection.style.display = "block";
        }

        // Переключение между Входом и Регистрацией
        document.getElementById("toggleAuthMode").addEventListener("click", function(e) {
            e.preventDefault();
            isLoginMode = !isLoginMode;
            document.getElementById("authTitle").innerText = isLoginMode ? "Вход" : "Регистрация";
            document.getElementById("btnSubmitAuth").innerText = isLoginMode ? "Войти" : "Зарегистрироваться";
            this.innerText = isLoginMode ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти";
        });

        // Обработка нажатия кнопки Войти/Зарегистрироваться
        document.getElementById("btnSubmitAuth").addEventListener("click", function() {
            let email = document.getElementById("authEmail").value.trim();
            let password = document.getElementById("authPassword").value.trim();
            let errorSpan = document.getElementById("authError");
            errorSpan.innerText = "";

            let endpoint = isLoginMode ? "/api/login" : "/api/register";

            fetch(`http://127.0.0.1:8000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: email, password: password })
            })
            .then(async response => {
                let data = await response.json();
                if (!response.ok) throw new Error(data.detail || "Ошибка");
                return data;
            })
            .then(data => {
                if (isLoginMode) {
                    localStorage.setItem("userId", data.user_id);
                    localStorage.setItem("userEmail", email);
                    window.location.reload(); 
                } else {
                    alert("Регистрация успешна! Теперь нажмите Войти.");
                    document.getElementById("toggleAuthMode").click(); 
                }
            })
            .catch(error => {
                errorSpan.innerText = error.message;
            });
        });

        // Выход из аккаунта
        document.getElementById("btnLogout").addEventListener("click", function() {
            localStorage.removeItem("userId");
            localStorage.removeItem("userEmail");
            window.location.reload();
        });
    }

});