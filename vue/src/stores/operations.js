import { Mutex } from 'async-mutex'

const mutex = new Mutex()

export async function runUpdate() {
  await mutex.runExclusive(async () => {
    await eel.update_kks_all()()
  })
}

export async function cancelUpdate() {
  await eel.update_cancel()()
}

export async function cancelSignals() {
  await eel.signals_data_cancel()()
}

export async function cancelGrid() {
  await eel.grid_data_cancel()()
}

