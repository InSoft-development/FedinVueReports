export async function getAnalogKKS(analogSensors) {
  analogSensors.value = await eel.get_analog_kks()()
}

export async function getDiscreteKKSByMask(discreteSensors, mask) {
  discreteSensors.value = await eel.get_discrete_kks_by_mask(mask)()
}

export async function getAnalogSignals(
  chosenSensors,
  chosenQuality,
  date,
  dataTable,
  dataTableRequested
) {
  let formatDate = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_analog_signals_data(chosenSensors, chosenQuality, formatDate)()
  if (typeof result === 'string') {
    dataTableRequested.value = false
    alert(result)
  }
  if (Array.isArray(result)) {
    dataTable.value = result
    dataTableRequested.value = true
  }
}

export async function getDiscreteSignals(
  chosenSensors,
  chosenValues,
  chosenQuality,
  date,
  dataTable,
  dataTableRequested
) {
  let formatDate = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_discrete_signals_data(
    chosenSensors,
    chosenValues,
    chosenQuality,
    formatDate
  )()
  if (typeof result === 'string') {
    dataTableRequested.value = false
    alert(result)
  }
  if (Array.isArray(result)) {
    dataTable.value = result
    dataTableRequested.value = true
  }
}

export async function getAnalogGrid(chosenSensors, dateBegin, dateEnd, interval, dimension,  dataTable, dataTableRequested, dataTableStatus) {
  let formatDateBegin = new Date(dateBegin.toString().split('GMT')[0] + ' UTC').toISOString()
  let formatDateEnd = new Date(dateEnd.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_analog_grid_data(
    chosenSensors,
    formatDateBegin,
    formatDateEnd,
    interval,
    dimension
  )()
  if (typeof result === 'string') {
    dataTableRequested.value = false
    alert(result)
  }
  if (Array.isArray(result)) {
    dataTable.value = result[0]
    dataTableStatus.value = result[1]
    dataTableRequested.value = true
  }
}

export async function getDiscreteGrid(chosenSensors, dateBegin, dateEnd, interval, dimension,  dataTable, dataTableRequested, dataTableStatus) {
  let formatDateBegin = new Date(dateBegin.toString().split('GMT')[0] + ' UTC').toISOString()
  let formatDateEnd = new Date(dateEnd.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_discrete_grid_data(
    chosenSensors,
    formatDateBegin,
    formatDateEnd,
    interval,
    dimension
  )()
  if (typeof result === 'string') {
    dataTableRequested.value = false
    alert(result)
  }
  if (Array.isArray(result)) {
    dataTable.value = result[0]
    dataTableStatus.value = result[1]
    dataTableRequested.value = true
  }
}

export async function getBounceSignals(templateSignal, date, interval, dimension, showSensors,  dataTable, dataTableRequested) {
  let formatDate = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_bounce_signals_data(
    templateSignal,
    formatDate,
    interval,
    dimension,
    showSensors
  )()
  if (typeof result === 'string') {
    dataTableRequested.value = false
    alert(result)
  }
  if (Array.isArray(result)) {
    dataTable.value = result
    dataTableRequested.value = true
    console.log(dataTable.value)
  }
}
