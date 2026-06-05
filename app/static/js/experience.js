/* ==========================================================================
   EXPERIENCE.JS — Controls Interactive Graphs, Tables, and Slideshows
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
    // ════════════════ Parse Database Experience Data ════════════════
    const dbDataEl = document.getElementById("experience-db-data");
    let dbData = [];
    if (dbDataEl) {
        try {
            dbData = JSON.parse(dbDataEl.textContent);
        } catch (e) {
            console.error("Error parsing experience data:", e);
        }
    }

    const salesData = {};
    const productData = {};

    dbData.forEach(c => {
        const slug = c.slug;
        salesData[slug] = {
            months: c.months.map(m => m.month),
            products: c.months.map(m => m.product_focus),
            targets: c.months.map(m => m.target),
            sales: c.months.map(m => m.sales),
            metric_type: c.metric_type
        };

        productData[slug] = c.products.map(p => {
            const price = p.price || 0;
            const targetQty = p.target || 0;
            const salesQty = p.sales || 0;
            return {
                name: p.name,
                pack: p.pack,
                price: price,
                target: targetQty,
                target_val: targetQty * price,
                sales: salesQty,
                sales_val: salesQty * price
            };
        });
    });

    let currentCompany = dbData.length > 0 ? dbData[0].slug : "integrace";
    let currentViewType = "month";

    // Chart.js Default Configurations
    Chart.defaults.color = "#737373";
    Chart.defaults.font.family = "'Outfit', sans-serif";

    // Initialize Chart
    const ctx = document.getElementById("salesChart")?.getContext("2d");
    let salesChart = null;

    if (ctx && salesData[currentCompany]) {
        const isCurrency = salesData[currentCompany].metric_type === "currency";
        salesChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: salesData[currentCompany].months,
                datasets: [
                    {
                        label: isCurrency ? "Monthly Target (INR)" : "Monthly Target (Packs)",
                        data: salesData[currentCompany].targets,
                        borderColor: "rgba(255, 255, 255, 0.4)",
                        borderWidth: 2,
                        borderDash: [5, 5],
                        backgroundColor: "transparent",
                        pointBackgroundColor: "rgba(255, 255, 255, 0.7)",
                        pointBorderColor: "rgba(255, 255, 255, 0.9)",
                        pointRadius: 3,
                        pointHoverRadius: 6,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: isCurrency ? "Actual Sales (INR)" : "Actual Sales (Packs)",
                        data: salesData[currentCompany].sales,
                        borderColor: "#7AB7FF",
                        borderWidth: 3,
                        backgroundColor: "rgba(122, 183, 255, 0.15)",
                        pointBackgroundColor: "#7AB7FF",
                        pointBorderColor: "#FFFFFF",
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 8,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            boxWidth: 12,
                            padding: 20,
                            font: {
                                weight: "600"
                            }
                        }
                    },
                    tooltip: {
                        padding: 12,
                        backgroundColor: "#1A1A1A",
                        titleColor: "#FFF",
                        bodyColor: "#A6A6A6",
                        borderColor: "rgba(255, 255, 255, 0.08)",
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    const cType = salesData[currentCompany]?.metric_type;
                                    if (cType === "currency") {
                                        label += "₹" + context.parsed.y.toLocaleString();
                                    } else {
                                        label += context.parsed.y.toLocaleString() + " units";
                                    }
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "rgba(255, 255, 255, 0.03)"
                        },
                        ticks: {
                            callback: function(value) {
                                const cType = salesData[currentCompany]?.metric_type;
                                if (cType === "currency") {
                                    return "₹" + (value / 100000).toFixed(1) + " L";
                                } else {
                                    return value.toLocaleString() + " units";
                                }
                            }
                        }
                    }
                }
            }
        });
    }

    // ════════════════ Render metrics table ════════════════
    const tableHeader = document.querySelector("#metricsTable thead tr");
    const tableBody = document.getElementById("metricsTableBody");

    function renderTable(company, viewType = "month") {
        if (!tableBody || !tableHeader || !salesData[company]) return;
        tableBody.innerHTML = "";
        const isCurrency = salesData[company].metric_type === "currency";
        
        if (viewType === "month") {
            // Render month-wise
            tableHeader.innerHTML = `
                <th>Month</th>
                <th>Product Focus</th>
                <th>${isCurrency ? "Target Value" : "Target Qty"}</th>
                <th>${isCurrency ? "Sales Value" : "Sales Qty"}</th>
                <th>Achievement %</th>
                <th>Status</th>
            `;
            
            const data = salesData[company];
            let totalTarget = 0;
            let totalSales = 0;

            for (let i = 0; i < data.months.length; i++) {
                const target = data.targets[i];
                const sale = data.sales[i];
                const achievement = target > 0 ? ((sale / target) * 100).toFixed(1) : "0.0";
                const isTargetMet = sale >= target;
                const badgeClass = isTargetMet ? "badge-green" : "badge-orange";
                const badgeText = isTargetMet ? "Met" : "90%+ Ach.";

                totalTarget += target;
                totalSales += sale;

                const targetText = isCurrency ? "₹" + target.toLocaleString() : target.toLocaleString() + " units";
                const salesText = isCurrency ? "₹" + sale.toLocaleString() : sale.toLocaleString() + " units";

                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${data.months[i]}</strong></td>
                    <td>${data.products[i]}</td>
                    <td>${targetText}</td>
                    <td>${salesText}</td>
                    <td><strong>${achievement}%</strong></td>
                    <td><span class="achievement-badge ${badgeClass}">${badgeText}</span></td>
                `;
                tableBody.appendChild(tr);
            }

            // Add Financial Year Total Row
            const overallAchievement = totalTarget > 0 ? ((totalSales / totalTarget) * 100).toFixed(1) : "0.0";
            const totalTargetText = isCurrency ? "₹" + totalTarget.toLocaleString() : totalTarget.toLocaleString() + " units";
            const totalSalesText = isCurrency ? "₹" + totalSales.toLocaleString() : totalSales.toLocaleString() + " units";
            const totalTr = document.createElement("tr");
            totalTr.className = "row-total";
            totalTr.innerHTML = `
                <td>FY TOTAL</td>
                <td>All Focus Products</td>
                <td>${totalTargetText}</td>
                <td>${totalSalesText}</td>
                <td>${overallAchievement}%</td>
                <td><span class="achievement-badge badge-green">100%+ FY Avg</span></td>
            `;
            tableBody.appendChild(totalTr);
            
        } else {
            // Render product-wise
            tableHeader.innerHTML = `
                <th>Product Name</th>
                <th>Pack Size</th>
                <th>${isCurrency ? "Target Value" : "Target Qty (YTD)"}</th>
                <th>${isCurrency ? "Sales Value" : "Sales Qty (YTD)"}</th>
                <th>Achievement %</th>
                <th>Status</th>
            `;
            
            const products = productData[company];
            let totalTarget = 0;
            let totalSales = 0;

            products.forEach(p => {
                const target = isCurrency ? p.target_val : p.target;
                const sale = isCurrency ? p.sales_val : p.sales;
                const achievement = target > 0 ? ((sale / target) * 100).toFixed(1) : "0.0";
                const isTargetMet = sale >= target;
                const badgeClass = isTargetMet ? "badge-green" : "badge-orange";
                const badgeText = isTargetMet ? "Met" : "90%+ Ach.";

                totalTarget += target;
                totalSales += sale;

                const targetText = isCurrency ? "₹" + target.toLocaleString() : target.toLocaleString() + " units";
                const salesText = isCurrency ? "₹" + sale.toLocaleString() : sale.toLocaleString() + " units";

                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${p.name}</strong></td>
                    <td><span class="pack-badge" style="background: rgba(255,255,255,0.03); padding: 4px 8px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.8rem; color: var(--text-secondary);">${p.pack}</span></td>
                    <td>${targetText}</td>
                    <td>${salesText}</td>
                    <td><strong>${achievement}%</strong></td>
                    <td><span class="achievement-badge ${badgeClass}">${badgeText}</span></td>
                `;
                tableBody.appendChild(tr);
            });

            // Add Overall Total Row
            const overallAchievement = totalTarget > 0 ? ((totalSales / totalTarget) * 100).toFixed(1) : "0.0";
            const totalTargetText = isCurrency ? "₹" + totalTarget.toLocaleString() : totalTarget.toLocaleString() + " units";
            const totalSalesText = isCurrency ? "₹" + totalSales.toLocaleString() : totalSales.toLocaleString() + " units";
            const totalTr = document.createElement("tr");
            totalTr.className = "row-total";
            totalTr.innerHTML = `
                <td>TOTAL YTD</td>
                <td>All Packs</td>
                <td>${totalTargetText}</td>
                <td>${totalSalesText}</td>
                <td>${overallAchievement}%</td>
                <td><span class="achievement-badge badge-green">${overallAchievement >= 100 ? 'Met' : '90%+ Ach.'}</span></td>
            `;
            tableBody.appendChild(totalTr);
        }
    }

    // Initial render
    renderTable(currentCompany, currentViewType);

    // ════════════════ Analytics Tab switching ════════════════
    const tabButtons = document.querySelectorAll(".analytics-tab");
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            tabButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            currentCompany = button.getAttribute("data-company");

            // Update Chart
            if (salesChart && salesData[currentCompany]) {
                const isCurrency = salesData[currentCompany].metric_type === "currency";
                salesChart.data.labels = salesData[currentCompany].months;
                salesChart.data.datasets[0].data = salesData[currentCompany].targets;
                salesChart.data.datasets[1].data = salesData[currentCompany].sales;
                if (!isCurrency) {
                    salesChart.data.datasets[0].label = "Monthly Target (Packs)";
                    salesChart.data.datasets[1].label = "Actual Sales (Packs)";
                } else {
                    salesChart.data.datasets[0].label = "Monthly Target (INR)";
                    salesChart.data.datasets[1].label = "Actual Sales (INR)";
                }
                salesChart.update();
            }

            // Update Table
            renderTable(currentCompany, currentViewType);
        });
    });

    // ════════════════ View Toggle (Month-wise vs Product-wise) ════════════════
    const viewToggleBtns = document.querySelectorAll(".view-toggle-btn");
    viewToggleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            viewToggleBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            currentViewType = btn.getAttribute("data-view-type");
            renderTable(currentCompany, currentViewType);
        });
    });

    // ════════════════ Document Toggle (Company Selector for Verification Docs) ════════════════
    const docToggles = document.querySelectorAll("[data-company-doc]");
    docToggles.forEach(toggle => {
        toggle.addEventListener("click", () => {
            const parent = toggle.closest(".appointment-doc-card");
            parent.querySelectorAll("[data-company-doc]").forEach(btn => btn.classList.remove("active"));
            toggle.classList.add("active");

            const company = toggle.getAttribute("data-company-doc");
            parent.querySelectorAll(".doc-company-group").forEach(group => {
                if (group.id === `doc-${company}-group`) {
                    group.style.display = "block";
                } else {
                    group.style.display = "none";
                }
            });
        });
    });

    // ════════════════ Document Type Toggle (Appointment / Offer / Pay Slip) ════════════════
    const docTypeBtns = document.querySelectorAll(".doc-type-btn");
    docTypeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const parent = btn.closest(".appointment-doc-card");
            parent.querySelectorAll(".doc-type-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const selectedType = btn.getAttribute("data-doc-type");
            
            parent.querySelectorAll(".doc-type-item").forEach(item => {
                if (item.id.endsWith(selectedType)) {
                    item.style.display = "block";
                    item.classList.add("active");
                } else {
                    item.style.display = "none";
                    item.classList.remove("active");
                }
            });
        });
    });

    // ════════════════ Document Toggle (Incentives) ════════════════
    const incToggles = document.querySelectorAll("[data-company-inc]");
    incToggles.forEach(toggle => {
        toggle.addEventListener("click", () => {
            const parent = toggle.closest(".incentives-doc-card");
            parent.querySelectorAll("[data-company-inc]").forEach(btn => btn.classList.remove("active"));
            toggle.classList.add("active");

            const company = toggle.getAttribute("data-company-inc");
            parent.querySelectorAll(".incentive-slide-container").forEach(slider => {
                if (slider.id === `inc-${company}-slider`) {
                    slider.classList.remove("hidden");
                } else {
                    slider.classList.add("hidden");
                }
            });
        });
    });

    // ════════════════ Incentives Slide Gallery Logic ════════════════
    const sliders = document.querySelectorAll(".incentive-slide-container");
    sliders.forEach(slider => {
        const slides = slider.querySelectorAll(".incentive-slide");
        if (slides.length <= 1) return;

        const prevBtn = slider.querySelector(".prev-slide");
        const nextBtn = slider.querySelector(".next-slide");
        const counterEl = slider.querySelector(".current-num");
        let activeIdx = 0;

        function updateSlider() {
            slides.forEach((slide, idx) => {
                if (idx === activeIdx) {
                    slide.classList.add("active");
                } else {
                    slide.classList.remove("active");
                }
            });
            if (counterEl) counterEl.textContent = activeIdx + 1;
        }

        if (prevBtn) {
            prevBtn.addEventListener("click", () => {
                activeIdx = (activeIdx - 1 + slides.length) % slides.length;
                updateSlider();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener("click", () => {
                activeIdx = (activeIdx + 1) % slides.length;
                updateSlider();
            });
        }
    });
});
