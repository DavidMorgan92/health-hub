(() => {
  if (!window.FullCalendar) return;

  document.querySelectorAll('[data-plan-calendar]:not([data-initialized])').forEach((calendarElement) => {
    const events = JSON.parse(
      document.getElementById(calendarElement.dataset.eventsId).textContent,
    );
    const eventModalElement = calendarElement.parentElement.querySelector('[data-plan-event-modal]');
    const eventInstructionsElement = eventModalElement.querySelector('[data-plan-event-instructions]');
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
        if (!instructions) return;

        eventInstructionsElement.textContent = instructions;
        const eventModal = bootstrap.Modal.getOrCreateInstance(eventModalElement);
        eventModal.show();
      },
    });
    calendarElement.dataset.initialized = 'true';
    calendar.render();
  });
})();
