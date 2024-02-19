export async function getAnalogKKS(analogSensors) {
  analogSensors.value = await eel.get_analog_kks()()
}

export async function getDiscreteKKSByMask(discreteSensors, mask) {
  discreteSensors.value = await eel.get_discrete_kks_by_mask(mask)()
}

export async function getAnalogSignals(chosenSensors, chosenQuality, date, dataTable) {
  let formatDate = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_analog_signals_data(chosenSensors, chosenQuality, formatDate)()
  if (typeof result === 'string') alert(result)
  if (Array.isArray(result)) {
    dataTable.value = result
  }
}
