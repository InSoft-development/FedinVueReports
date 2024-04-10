import { Mutex } from 'async-mutex'

const mutex = new Mutex()

/***
 * Процедура запуска обновления файла тегов kks_all.csv
 * @returns {Promise<void>}
 */
export async function runUpdate() {
  await mutex.runExclusive(async () => {
    await eel.update_kks_all()()
  })
}

/***
 * Процедура отмены пользователем обновления файла тегов kks_all.csv
 * @returns {Promise<void>}
 */
export async function cancelUpdate() {
  await eel.update_cancel()()
}

/***
 * Процедура отмены пользователем запроса среза сигналов
 * @returns {Promise<void>}
 */
export async function cancelSignals() {
  await eel.signals_data_cancel()()
}

/***
 * Процедура отмены пользователем запроса сетки сигналов
 * @returns {Promise<void>}
 */
export async function cancelGrid() {
  await eel.grid_data_cancel()()
}

/***
 * Процедура отмены пользователем запроса дребезга сигналов
 * @returns {Promise<void>}
 */
export async function cancelBounce() {
  await eel.bounce_data_cancel()()
}

/***
 * Процедура изменения конфигурации клиента OPC UA
 * @param ipOPC
 * @param portOPC
 * @returns {Promise<void>}
 */
export async function changeOpcServerConfig(ipOPC, portOPC) {
  await eel.change_opc_server_config(ipOPC, portOPC)()
}
