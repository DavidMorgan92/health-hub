(() => {
  const editor = document.querySelector('[data-plan-editor]');
  const calendarElement = document.querySelector('[data-create-plan-calendar]');
  const eventsInput = editor?.querySelector('[data-events-input]');
  const eventList = editor?.querySelector('[data-event-list]');
  const eventFields = editor?.querySelector('[data-event-fields]');
  const eventDataElement = document.getElementById('plan-event-data');

  if (!editor || !calendarElement || !eventsInput || !eventList || !eventFields || !eventDataElement) return;

  const numberFields = new Set([
    'start_offset_days',
    'duration_days',
    'recurrence_interval_days',
    'recurrence_count',
  ]);
  const optionalNumberFields = new Set(['recurrence_interval_days', 'recurrence_count']);
  const defaultEvent = {
    title: '',
    instructions: '',
    start_offset_days: 0,
    duration_days: 1,
    recurrence_interval_days: null,
    recurrence_count: null,
  };
  let events = JSON.parse(eventDataElement.textContent || '[]');
  let selectedIndex = events.length ? 0 : -1;

  const normalizeEvent = (event) => ({
    ...defaultEvent,
    ...event,
    start_offset_days: Number(event.start_offset_days ?? 0),
    duration_days: Number(event.duration_days ?? 1),
    recurrence_interval_days: event.recurrence_interval_days === '' || event.recurrence_interval_days == null
      ? null
      : Number(event.recurrence_interval_days),
    recurrence_count: event.recurrence_count === '' || event.recurrence_count == null
      ? null
      : Number(event.recurrence_count),
  });

  events = events.map(normalizeEvent);

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const addDays = (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  };

  const calendarEvents = () => {
    const today = new Date();
    return events.flatMap((event, eventIndex) => {
      const occurrences = [];
      const interval = event.recurrence_interval_days || 0;
      const horizon = 365;
      for (let occurrence = 0; occurrence <= horizon; occurrence += 1) {
        if (event.recurrence_count != null && occurrence >= event.recurrence_count) break;
        const offset = event.start_offset_days + occurrence * interval;
        if (offset > horizon) break;
        const start = addDays(today, offset);
        const end = addDays(start, event.duration_days || 1);
        occurrences.push({
          id: `${eventIndex}-${occurrence}`,
          title: event.title || `Event ${eventIndex + 1}`,
          start: formatDate(start),
          end: formatDate(end),
          allDay: true,
          color: '#2563eb',
          extendedProps: { instructions: event.instructions || '' },
        });
        if (!interval) break;
      }
      return occurrences;
    });
  };

  const calendar = new FullCalendar.Calendar(calendarElement, {
    initialView: 'dayGridMonth',
    firstDay: 1,
    height: 'auto',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,listMonth',
    },
    events: calendarEvents(),
  });
  calendar.render();

  const sync = () => {
    eventsInput.value = JSON.stringify(events);
    calendar.removeAllEvents();
    calendar.addEventSource(calendarEvents());
  };

  const renderFields = () => {
    const hasSelection = selectedIndex >= 0 && events[selectedIndex];
    eventFields.querySelectorAll('[data-event-field]').forEach((field) => {
      field.disabled = !hasSelection;
      field.value = hasSelection && events[selectedIndex][field.dataset.eventField] != null
        ? events[selectedIndex][field.dataset.eventField]
        : '';
    });
    editor.querySelector('[data-delete-event]').disabled = !hasSelection;
  };

  const renderList = () => {
    eventList.replaceChildren();
    events.forEach((event, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = `list-group-item list-group-item-action${index === selectedIndex ? ' active' : ''}`;
      button.textContent = event.title || `Event ${index + 1}`;
      button.addEventListener('click', () => {
        selectedIndex = index;
        renderList();
        renderFields();
      });
      eventList.appendChild(button);
    });
    renderFields();
  };

  eventFields.querySelectorAll('[data-event-field]').forEach((field) => {
    field.addEventListener('input', () => {
      if (selectedIndex < 0) return;
      const name = field.dataset.eventField;
      const value = field.value;
      events[selectedIndex][name] = numberFields.has(name)
        ? (value === '' && optionalNumberFields.has(name) ? null : Number(value))
        : value;
      if (name === 'title') renderList();
      sync();
    });
  });

  editor.querySelector('[data-add-event]').addEventListener('click', () => {
    events.push({ ...defaultEvent });
    selectedIndex = events.length - 1;
    renderList();
    sync();
    eventFields.querySelector('[data-event-field="title"]').focus();
  });

  editor.querySelector('[data-delete-event]').addEventListener('click', () => {
    if (selectedIndex < 0) return;
    events.splice(selectedIndex, 1);
    selectedIndex = Math.min(selectedIndex, events.length - 1);
    renderList();
    sync();
  });

  editor.addEventListener('submit', sync);
  renderList();
  sync();
})();
