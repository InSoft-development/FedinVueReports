<script>
import { ref } from 'vue'
import { getBounceSignals } from '../stores'

export default {
  name: 'BounceSignals',
  setup() {
    const templateText = ref('\\.*')

    const dateTime = ref()
    const disableTime = ref(false)

    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const progressBarBounceSignals = ref('0')
    const progressBarBounceSignalsActive = ref(false)

    const countShowSensors = ref(10)

    const currentDateChecked = ref(false)

    const dataTable = ref()
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      dataTableStartRequested.value = true
      dateTimeBeginReport.value = new Date().toLocaleString()
      if (!dateTime.value || templateText.value === '') {
        alert('Не заполнены параметры запроса!')
        return
      }

      progressBarBounceSignalsActive.value = true
      progressBarBounceSignals.value = '0'

      await getBounceSignals(
        templateText.value,
        dateTime.value,
        interval.value,
        intervalRadio.value,
        countShowSensors.value,
        dataTable,
        dataTableRequested
      )

      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarBounceSignals.value = '100'
      progressBarBounceSignalsActive.value = false
    }

    function setProgressBarBounceSignals(count) {
      progressBarBounceSignals.value = String(count)
    }
    window.eel.expose(setProgressBarBounceSignals, 'setProgressBarBounceSignals')

    function onChangeCheckbox() {
      if (!disableTime.value) dateTime.value = new Date()
      disableTime.value = !disableTime.value
    }

    return {
      templateText,
      dateTime,
      disableTime,
      dateTimeBeginReport,
      dateTimeEndReport,
      interval,
      intervalRadio,
      progressBarBounceSignals,
      progressBarBounceSignalsActive,
      countShowSensors,
      currentDateChecked,
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
      onRequestButtonClick,
      setProgressBarBounceSignals,
      onChangeCheckbox
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Дребезг сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <label for="template-text">Введите шаблон кода сигнала</label>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
          <InputText
            id="template-text"
            type="text"
            v-model="templateText"
            :pt="{ root: { class: 'col-md-12' } }"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-4">
          <label for="calendar-date">Введите дату</label>
        </div>
      </div>
      <div class="row">
        <div class="col-4" style="padding-bottom: 20px">
          <Calendar
            id="calendar-date"
            v-model="dateTime"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
            :disabled="disableTime"
          >
          </Calendar>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="day" name="day" value="day" />
          <label for="day">&nbsp;&nbsp;День</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="hour" name="hour" value="hour" />
          <label for="hour">&nbsp;&nbsp;Час</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="minute" name="minute" value="minute" />
          <label for="minute">&nbsp;&nbsp;Минута</label>
        </div>
        <div class="col-md-auto">
          <RadioButton v-model="intervalRadio" inputId="second" name="second" value="second" />
          <label for="second">&nbsp;&nbsp;Секунда</label>
        </div>
        <div class="col-md-auto">
          <Checkbox
            id="current-date-checked"
            v-model="currentDateChecked"
            :binary="true"
            @change="onChangeCheckbox"
          ></Checkbox>
          <label for="current-date-checked">Использовать текущее время</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="interval">Интервал</label>
        </div>
        <div class="col">
          <label for="show-sensors">Количество показываемых датчиков</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <InputNumber
            v-model="interval"
            id="interval"
            input-id="interval"
            mode="decimal"
            show-buttons
            :min="1"
            :step="1"
            :allow-empty="false"
            :aria-label="interval"
          >
          </InputNumber>
        </div>
        <div class="col" style="padding-bottom: 20px">
          <InputNumber
            v-model="countShowSensors"
            id="show-sensors"
            input-id="countShowSensors"
            mode="decimal"
            show-buttons
            :min="1"
            :step="1"
            :allow-empty="false"
            :aria-label="countShowSensors"
          >
          </InputNumber>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Button @click="onRequestButtonClick">Запрос</Button>
        </div>
      </div>
      <div class="row" v-if="dataTableStartRequested">
        Старт построения отчета: {{ dateTimeBeginReport }}
      </div>
      <div class="row" v-if="progressBarBounceSignalsActive">
        <div class="col">
          <ProgressBar :value="progressBarBounceSignals"></ProgressBar>
        </div>
      </div>
      <div class="row" style="padding-bottom: 20px">
        <div class="card" v-if="dataTableRequested">
          <DataTable
            :value="dataTable"
            scrollable="true"
            scrollHeight="1000px"
            columnResizeMode="fit"
            showGridlines="true"
            tableStyle="min-width: 50rem"
          >
            <Column field="Наименование датчика" header="Наименование датчика" sortable></Column>
            <Column field="Частота" header="Частота" sortable></Column>
          </DataTable>
        </div>
      </div>
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style></style>
