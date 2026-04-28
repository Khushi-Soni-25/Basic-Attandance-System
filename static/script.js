let records = {};

const dateInput = document.getElementById("dateInput");
const statusInput = document.getElementById("statusInput");
const noteInput = document.getElementById("noteInput");

document.addEventListener("DOMContentLoaded", () => {
  const today = new Date().toISOString().split("T")[0];
  dateInput.value = today;

  document.getElementById("todayDate").innerText = formatDate(today);

  loadRecords();
  loadProfileInfo();
});

function changePage(pageId, clickedBtn = null) {
  document.querySelectorAll(".page").forEach(page => {
    page.classList.remove("active-page");
  });

  document.getElementById(pageId).classList.add("active-page");

  if (clickedBtn) {
    document.querySelectorAll(".nav-btn").forEach(btn => {
      btn.classList.remove("active-nav");
    });

    clickedBtn.classList.add("active-nav");
  }
}

function quickStatus(status) {
  statusInput.value = status;
}

async function loadRecords() {
  try {
    const response = await fetch("/get-records");
    records = await response.json();

    updateDashboard();
    showRecentRecords();
    showAllRecords();
  } catch (error) {
    console.error("Error loading records:", error);
  }
}

async function saveRecord() {
  const date = dateInput.value;
  const status = statusInput.value;
  const note = noteInput.value.trim();

  if (!date) {
    alert("Please select a date.");
    return;
  }

  const record = {
    date: date,
    status: status,
    note: note
  };

  try {
    const response = await fetch("/save-record", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(record)
    });

    if (response.ok) {
      noteInput.value = "";
      await loadRecords();
      alert("Attendance saved successfully!");
      changePage("dashboardPage", document.querySelectorAll(".nav-btn")[0]);
    }
  } catch (error) {
    console.error("Error saving record:", error);
    alert("Something went wrong while saving.");
  }
}

async function loadProfileInfo() {
  try {
    const response = await fetch("/profile-info");

    if (!response.ok) {
      return;
    }

    const profile = await response.json();

    document.getElementById("profileFullName").innerText =
      profile.full_name || profile.username || "Office Attendance Tracker";
    document.getElementById("profileCompanyName").innerText =
      profile.company_name || "Personal attendance record app";
    document.getElementById("profileUsername").innerText =
      profile.username ? `@${profile.username}` : "Profile";
  } catch (error) {
    console.error("Error loading profile:", error);
  }
}

function updateDashboard() {
  let fullDays = 0;
  let halfLeaves = 0;
  let holidays = 0;

  Object.values(records).forEach(record => {
    if (record.status === "Present") {
      fullDays++;
    }

    if (
      record.status === "First Half Leave" ||
      record.status === "Second Half Leave"
    ) {
      halfLeaves++;
    }

    if (record.status === "Holiday") {
      holidays++;
    }
  });

  document.getElementById("fullDays").innerText = fullDays;
  document.getElementById("halfLeaves").innerText = halfLeaves;
  document.getElementById("holidays").innerText = holidays;

  const today = new Date().toISOString().split("T")[0];

  if (records[today]) {
    document.getElementById("todayStatus").innerText = records[today].status;
  } else {
    document.getElementById("todayStatus").innerText = "No record yet";
  }
}

function showRecentRecords() {
  const recentBox = document.getElementById("recentRecords");
  const sortedDates = Object.keys(records).sort().reverse().slice(0, 4);

  if (sortedDates.length === 0) {
    recentBox.innerHTML = `<div class="empty">No records added yet.</div>`;
    return;
  }

  recentBox.innerHTML = sortedDates.map(date => {
    return createRecordCard(date, records[date]);
  }).join("");
}

function showAllRecords() {
  const allBox = document.getElementById("allRecords");
  const sortedDates = Object.keys(records).sort().reverse();

  if (sortedDates.length === 0) {
    allBox.innerHTML = `<div class="empty">No records found.</div>`;
    return;
  }

  allBox.innerHTML = sortedDates.map(date => {
    return createRecordCard(date, records[date]);
  }).join("");
}

function createRecordCard(date, record) {
  const className = getStatusClass(record.status);

  return `
    <div class="record-card">
      <div>
        <h3>${formatDate(date)}</h3>
        <p>${record.note || "No note added"}</p>
      </div>

      <span class="status-badge ${className}">
        ${record.status}
      </span>
    </div>
  `;
}

function getStatusClass(status) {
  if (status === "Present") return "full-day";
  if (status === "First Half Leave") return "first-half-leave";
  if (status === "Second Half Leave") return "second-half-leave";
  if (status === "Holiday") return "holiday";
  if (status === "Absent") return "absent";
  return "";
}

function formatDate(dateString) {
  const date = new Date(dateString);

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  });
}
