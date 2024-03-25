import { Mutex } from 'async-mutex'

const mutex = new Mutex()

export async function getServerConfig(configServer, checkFileActive) {
  let result = await eel.get_server_config()()
  configServer.value = result[0]
  checkFileActive.value = result[1]
}

export async function getIpAndPortConfig(ipOPC, portOPC) {
  let result = await eel.get_ip_port_config()()
  ipOPC.value = result[0]
  portOPC.value = result[1]
}

export async function getLastUpdateFileKKS(lastUpdateFileKKS) {
  lastUpdateFileKKS.value = await eel.get_last_update_file_kks()()
}

export async function getTypesOfSensors(typesOptions) {
  typesOptions.value[0].options = await eel.get_types_of_sensors()()
}

export async function getAnalogKKS(analogSensors) {
  analogSensors.value = await eel.get_analog_kks()()
}

export async function getDiscreteKKSByMask(discreteSensors, mask) {
  discreteSensors.value = await eel.get_discrete_kks_by_mask(mask)()
}

export async function getKKSFilterByMasks(options, types, masks) {
  await mutex.runExclusive(async () => {
    let masksRequestArray = Array()
    let lastKKS = ''

    for (let i = 0; i < masks.length; i++) {
      if (!(await eel.get_kks_tag_exist(masks[i])())) {
        masksRequestArray.push(masks[i])
      } else {
        if (i == masks.length - 1) lastKKS = masks[i]
      }
    }

    // for (let mask of masks){
    //   if (!(await eel.get_kks_tag_exist(mask)()))
    //     masksRequestArray.push(mask)
    // }

    let result = await eel.get_kks_by_masks(types, masksRequestArray)()
    if (lastKKS.length != 0) result.unshift(lastKKS)
    options.value[1].options = result
  })
}

export async function getKKSByMasksForTable(chosenSensors, types, sensorsAndTemplate) {
  await mutex.runExclusive(async () => {
    let kks = Array()
    let masks = Array()
    for (let element of sensorsAndTemplate) {
      if (await eel.get_kks_tag_exist(element)()) kks.push(element)
      else masks.push(element)
    }
    let result = await eel.get_kks(types, masks, kks)()
    chosenSensors.value = result
  })
}

export async function getSignals(
  types,
  sensorsAndTemplate,
  qualities,
  date,
  dateDeepOfSearch,
  dataTable,
  dataTableRequested
) {
  await mutex.runExclusive(async () => {
    let formatDate = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
    let formatDateDeepOfSearch = new Date(dateDeepOfSearch.toString().split('GMT')[0] + ' UTC').toISOString()
    let kks = Array()
    let masks = Array()
    for (let element of sensorsAndTemplate) {
      if (await eel.get_kks_tag_exist(element)()) kks.push(element)
      else masks.push(element)
    }

    let result = await eel.get_signals_data(types, masks, kks, qualities, formatDate, formatDateDeepOfSearch)()
    if (typeof result === 'string') {
      dataTableRequested.value = false
      alert(result)
    }
    if (Array.isArray(result)) {
      dataTable.value = result
      dataTableRequested.value = true
      console.log(result)
    }
  })
}

export async function getGrid(
  chosenSensors,
  dateBegin,
  dateEnd,
  interval,
  dimension,
  dataTable,
  dataTableRequested,
  dataTableStatus
) {
  let formatDateBegin = new Date(dateBegin.toString().split('GMT')[0] + ' UTC').toISOString()
  let formatDateEnd = new Date(dateEnd.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.get_grid_data(
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

export async function getAnalogGrid(
  chosenSensors,
  dateBegin,
  dateEnd,
  interval,
  dimension,
  dataTable,
  dataTableRequested,
  dataTableStatus
) {
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

export async function getDiscreteGrid(
  chosenSensors,
  dateBegin,
  dateEnd,
  interval,
  dimension,
  dataTable,
  dataTableRequested,
  dataTableStatus
) {
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

export async function getBounceSignals(
  templateSignal,
  date,
  interval,
  dimension,
  showSensors,
  dataTable,
  dataTableRequested
) {
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
