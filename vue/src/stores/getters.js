import { Mutex } from 'async-mutex'

const mutex = new Mutex()

/***
 * Процедура получения конфигурации сервера OPC UA и проверки файла kks_all.csv
 * @param configServer
 * @param checkFileActive
 * @returns {Promise<void>}
 */
export async function getServerConfig(configServer, checkFileActive) {
  let result = await eel.get_server_config()()
  configServer.value = result[0]
  checkFileActive.value = result[1]
}

/***
 * Процедура получения ip-адреса и порта клиента OPC UA
 * @param ipOPC
 * @param portOPC
 * @returns {Promise<void>}
 */
export async function getIpAndPortConfig(ipOPC, portOPC) {
  let result = await eel.get_ip_port_config()()
  ipOPC.value = result[0]
  portOPC.value = result[1]
}

/***
 * Процедура получения даты последнего обновления файла kks_all.csv
 * @param lastUpdateFileKKS
 * @returns {Promise<void>}
 */
export async function getLastUpdateFileKKS(lastUpdateFileKKS) {
  lastUpdateFileKKS.value = await eel.get_last_update_file_kks()()
}

/***
 * Процедура получения полей по умолчанию из конфига
 * @returns {Promise<void>}
 */
export async function getDefaultFields(defaultFields) {
  let result = await eel.get_default_fields()()
  if (typeof result === 'string') {
    Object.assign(defaultFields, {
      typesOfSensors: ['String', 'UInt32', 'Boolean', 'Float'],
      sensorsAndTemplateValue: ['Sochi2\\.GT\\.AM\\.\\S*-AM\\.Q?$'],
      quality: ['8 - (BNC) - ОТКАЗ СВЯЗИ (TIMEOUT)', '192 - (GOD) – ХОРОШ'],
      dateDeepOfSearch: new Date(),
      interval: 10,
      dimension: 'hour',
      countShowSensors: 10
    })
    alert(result)
  } else {
    Object.assign(defaultFields, result)
    defaultFields.dateDeepOfSearch = new Date(defaultFields.dateDeepOfSearch)
  }
}

/***
 * Процедура получения типов данных тегов файла kks_all.csv
 * @param typesOptions
 * @returns {Promise<void>}
 */
export async function getTypesOfSensors(typesOptions) {
  typesOptions.value[0].options = await eel.get_types_of_sensors()()
}

/***
 * Процедура получения аналоговых срезов KKS
 * @param analogSensors
 * @returns {Promise<void>}
 */
export async function getAnalogKKS(analogSensors) {
  analogSensors.value = await eel.get_analog_kks()()
}

/***
 * Процедура получения дискретных срезов KKS по маске шаблона
 * @param analogSensors
 * @returns {Promise<void>}
 */
export async function getDiscreteKKSByMask(discreteSensors, mask) {
  discreteSensors.value = await eel.get_discrete_kks_by_mask(mask)()
}

/***
 * Процедура фильтрации kks по маске во время их поиска и выбора шаблона
 * @param options
 * @param types
 * @param masks
 * @returns {Promise<void>}
 */
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

/***
 * Процедура получения тегов kks по маске шаблона
 * @param chosenSensors
 * @param types
 * @param sensorsAndTemplate
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса среза
 * @param types
 * @param sensorsAndTemplate
 * @param qualities
 * @param date
 * @param dateDeepOfSearch
 * @param dataTable
 * @param dataTableRequested
 * @returns {Promise<void>}
 */
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
    let formatDateDeepOfSearch = new Date(
      dateDeepOfSearch.toString().split('GMT')[0] + ' UTC'
    ).toISOString()
    let kks = Array()
    let masks = Array()
    for (let element of sensorsAndTemplate) {
      if (await eel.get_kks_tag_exist(element)()) kks.push(element)
      else masks.push(element)
    }

    let result = await eel.get_signals_data(
      types,
      masks,
      kks,
      qualities,
      formatDate,
      formatDateDeepOfSearch
    )()
    if (typeof result === 'string') {
      dataTableRequested.value = false
      alert(result)
    }
    if (Array.isArray(result)) {
      dataTable.value = result
      dataTableRequested.value = true
    }
  })
}

/***
 * Процедура выполения запроса сетки
 * @param chosenSensors
 * @param dateBegin
 * @param dateEnd
 * @param interval
 * @param dimension
 * @param dataTable
 * @param dataTableRequested
 * @param dataTableStatus
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса среза аналогового сигнала
 * @param chosenSensors
 * @param chosenQuality
 * @param date
 * @param dataTable
 * @param dataTableRequested
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса среза дискретного сигнала
 * @param chosenSensors
 * @param chosenValues
 * @param chosenQuality
 * @param date
 * @param dataTable
 * @param dataTableRequested
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса построения аналоговой сетки
 * @param chosenSensors
 * @param dateBegin
 * @param dateEnd
 * @param interval
 * @param dimension
 * @param dataTable
 * @param dataTableRequested
 * @param dataTableStatus
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса построения дискретной сетки
 * @param chosenSensors
 * @param dateBegin
 * @param dateEnd
 * @param interval
 * @param dimension
 * @param dataTable
 * @param dataTableRequested
 * @param dataTableStatus
 * @returns {Promise<void>}
 */
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

/***
 * Процедура выполнения запроса построения дребезга сигналов
 * @param templateSignal
 * @param date
 * @param interval
 * @param dimension
 * @param showSensors
 * @param dataTable
 * @param dataTableRequested
 * @returns {Promise<void>}
 */
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
  }
}
