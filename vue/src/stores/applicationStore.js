import { defineStore } from 'pinia'

export const useApplicationStore = defineStore('ApplicationStore', () => {
  const badCode = [
    'BadNoCommunication',
    'BadSensorFailure',
    'BadCommunicationFailure',
    'BadDeviceFailure',
    'UncertainLastUsableValue'
  ]

  const badNumericCode = [8, 16, 24, 28, 88]
  return {
    badCode,
    badNumericCode
  }
})
