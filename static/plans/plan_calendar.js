(() => {
  if (!window.FullCalendar) return;

  document.querySelectorAll('[data-plan-calendar]:not([data-initialized])').forEach((calendarElement) => {
    const events = JSON.parse(
      document.getElementById(calendarElement.dataset.eventsId).textContent,
    );
    const calendar = new FullCalendar.Calendar(calendarElement, {
      initialView: 'dayGridMonth',
      firstDay: 1,
      height: 'auto',
      headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,listMonth',
      },
      events,
      eventClick: (info) => {
        const instructions = info.event.extendedProps.instructions;
        if (instructions) window.alert(instructions);
      },
    });
    calendarElement.dataset.initialized = 'true';
    calendar.render();
  });
})();
