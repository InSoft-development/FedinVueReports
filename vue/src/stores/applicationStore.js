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

  const deltaTimeInSeconds = {
    day: 86400,
    hour: 3600,
    minute: 60,
    second: 1
  }

  const estimatedSliceRateInHours = 4500
  const estimatedGridRateInHours = 4630000
  const estimatedBounceRateInHours = 8676604126000
  const sliceTimeLimitInHours = 0.5
  const gridTimeLimitInHours = 0.5
  const bounceTimeLimitInHours = 0.5
  return {
    badCode,
    badNumericCode,
    deltaTimeInSeconds,
    estimatedSliceRateInHours,
    estimatedGridRateInHours,
    estimatedBounceRateInHours,
    sliceTimeLimitInHours,
    gridTimeLimitInHours,
    bounceTimeLimitInHours
  }
})
