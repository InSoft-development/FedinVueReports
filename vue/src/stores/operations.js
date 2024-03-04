import { Mutex } from 'async-mutex'

const mutex = new Mutex()

export async function runUpdate() {
  await mutex.runExclusive(async () => {
    await eel.update_kks_all()()
  })
}