<script>
import Multiselect from '@vueform/multiselect'
import { ref, onMounted } from 'vue'
import { getDiscreteKKSByMask, getDiscreteGrid } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'DiscreteGrid',
  components: { Multiselect },
  setup() {
    const applicationStore = useApplicationStore()

    const templateSignals = ref([
      '.*\\.state\\..*',
      '.*-icCV_.*\\.state\\..*',
      'Sochi2\\.GT\\.AM\\..*',
      'Sochi2\\..*',
      'Unit2\\..*'
    ])
    const chosenTemplate = ref('.*\\.state\\..*')

    const discreteSensors = ref([])
    const sensors = ref(null)
    const chosenSensors = ref([])

    const dateTimeBegin = ref()
    const dateTimeEnd = ref()

    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const progressBarDiscreteSignals = ref('0')
    const progressBarDiscreteSignalsActive = ref(false)

    const dataCodeTable = ref()
    const dataTable = ref()
    const dataTableStatus = ref()
    const columnsTable = ref([])
    const countOfDataTable = ref(0)
    const columnsTableArrayOfArray = ref([])
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    onMounted(async () => {
      sensors.value = null
      chosenSensors.value = []
      await getDiscreteKKSByMask(discreteSensors, chosenTemplate.value)
    })

    function onTemplateSignalsChange(val) {
      sensors.value = null
      chosenSensors.value = []
      getDiscreteKKSByMask(discreteSensors, val)
    }

    function onMultiselectSensorsChange(val) {
      chosenSensors.value = val
    }

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      dataTableStartRequested.value = true
      dateTimeBeginReport.value = new Date().toLocaleString()
      if (!chosenSensors.value.length || !dateTimeBegin.value || !dateTimeEnd.value) {
        alert('Не заполнены параметры запроса!')
        return
      }

      if (dateTimeEnd.value.getTime() < dateTimeBegin.value.getTime()) {
        alert('Дата конца должна быть больше даты начала')
        return
      }

      if (dateTimeEnd.value.getTime() === dateTimeBegin.value.getTime()) {
        alert('Дата конца не должна совпадать с датой начала')
        return
      }

      columnsTable.value = []
      columnsTableArrayOfArray.value = []
      let codeTableArray = Array()
      let columnsTableArray = [{'field': "Метка времени", 'header': "Метка времени"}]

      for (const [index, element] of chosenSensors.value.entries()){
        codeTableArray.push({'№': index, 'Обозначение сигнала': element})
        columnsTableArray.push({'field': String(index), 'header': String(index)})
      }

      dataCodeTable.value = codeTableArray
      columnsTable.value = columnsTableArray

      progressBarDiscreteSignalsActive.value = true
      progressBarDiscreteSignals.value = '0'
      await getDiscreteGrid(chosenSensors.value, dateTimeBegin.value, dateTimeEnd.value, interval.value, intervalRadio.value,  dataTable, dataTableRequested, dataTableStatus)

      countOfDataTable.value = Math.ceil(chosenSensors.value.length / 10)

      if (countOfDataTable.value === 1) columnsTableArrayOfArray.value.push(columnsTableArray)
      else {
        for (let i = 0; i < countOfDataTable.value; i++){
          if (i === 0)  columnsTableArrayOfArray.value.push(columnsTable.value.slice(0, 11))
          else {
            columnsTableArrayOfArray.value.push(columnsTable.value.slice(i * 10 + 1, i * 10 + 11))
            columnsTableArrayOfArray.value[i].unshift({'field': "Метка времени", 'header': "Метка времени"})
          }
        }
      }

      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarDiscreteSignals.value = '100'
      progressBarDiscreteSignalsActive.value = false
    }

     function setProgressBarDiscreteSignals(count) {
      progressBarDiscreteSignals.value = String(count)
    }
    window.eel.expose(setProgressBarDiscreteSignals, 'setProgressBarDiscreteSignals')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathAnalogGridCsv = 'discrete_grid.csv'
      link.setAttribute('download', pathAnalogGridCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'discrete_grid.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      return
    }

    function statusClass(index, field) {
      return [
        {
          'bg-danger text-white': applicationStore.badCode.includes(dataTableStatus.value[index][String(field)]),
          'bg-warning text-white': dataTableStatus.value[index][String(field)] === 'missed'
        }
      ]
    }

    return {
      templateSignals,
      chosenTemplate,
      onTemplateSignalsChange,
      discreteSensors,
      sensors,
      chosenSensors,
      onMultiselectSensorsChange,
      dateTimeBegin,
      dateTimeEnd,
      dateTimeBeginReport,
      dateTimeEndReport,
      interval,
      intervalRadio,
      progressBarDiscreteSignals,
      progressBarDiscreteSignalsActive,
      dataCodeTable,
      dataTable,
      dataTableStatus,
      columnsTable,
      countOfDataTable,
      columnsTableArrayOfArray,
      dataTableRequested,
      dataTableStartRequested,
      onRequestButtonClick,
      setProgressBarDiscreteSignals,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick,
      statusClass
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Сетка дискретных сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="templateSignals">Выберите шаблон кода сигнала</label>
          <Multiselect
            id="templateSignals"
            v-model="chosenTemplate"
            mode="single"
            :close-on-select="false"
            :searchable="false"
            :create-option="false"
            :options="templateSignals"
            placeholder="Выберите шаблон кода сигнала"
            limit="-1"
            :can-clear="false"
            @change="onTemplateSignalsChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="discreteSensors">тег (KKS)</label>
          <Multiselect
            id="discreteSensors"
            v-model="sensors"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="discreteSensors"
            placeholder="Выберите аналоговые датчики"
            limit="-1"
            @change="onMultiselectSensorsChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="calendar-date-begin">Введите дату начала</label>
        </div>
        <div class="col">
          <label for="calendar-date-end">Введите дату конца</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Calendar
            id="calendar-date-begin"
            v-model="dateTimeBegin"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
          >
          </Calendar>
        </div>
        <div class="col" style="padding-bottom: 20px">
          <Calendar
            id="calendar-date-end"
            v-model="dateTimeEnd"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
          >
          </Calendar>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="interval">Интервал</label>
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
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="day" name="day" value="day" />
          <label for="day">&nbsp;&nbsp;День</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="hour" name="hour" value="hour" />
          <label for="hour">&nbsp;&nbsp;Час</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="minute" name="minute" value="minute" />
          <label for="minute">&nbsp;&nbsp;Минута</label>
        </div>
        <div class="col">
          <RadioButton v-model="intervalRadio" inputId="second" name="second" value="second" />
          <label for="second">&nbsp;&nbsp;Секунда</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Button @click="onRequestButtonClick">Запрос</Button>
        </div>
        <div class="col" v-if="dataTableRequested">
          <Button @click="onButtonDownloadPdfClick">Загрузить отчет</Button>
        </div>
        <div class="col" v-if="dataTableRequested">
          <Button @click="onButtonDownloadCsvClick">Загрузить CSV</Button>
        </div>
      </div>
      <div class="row" v-if="dataTableStartRequested">
        Старт построения отчета: {{ dateTimeBeginReport }}
      </div>
      <div class="row" v-if="progressBarDiscreteSignalsActive">
        <div class="col">
          <ProgressBar :value="progressBarDiscreteSignals"></ProgressBar>
        </div>
      </div>
      <div class="row" style="padding-bottom: 20px">
        <div class="card" v-if="dataTableRequested">
          <DataTable
            :value="dataCodeTable"
            scrollable="true"
            scrollHeight="1000px"
            columnResizeMode="fit"
            showGridlines="true"
            tableStyle="min-width: 50rem"
          >
            <Column
              field="№"
              header="№"
              sortable
              style="width: 35%"
            ></Column>
            <Column
              field="Обозначение сигнала"
              header="Обозначение сигнала"
              sortable
              style="width: 30%"
            ></Column>
          </DataTable>
        </div>
      </div>
      <div class="row" style="padding-bottom: 20px">
        <template v-for="i in countOfDataTable">
          <div style="padding-bottom: 20px">
            <div class="card" v-if="dataTableRequested">
              <DataTable
                :value="dataTable"
                scrollable="true"
                scrollHeight="1000px"
                columnResizeMode="fit"
                showGridlines="true"
                :virtualScrollerOptions="{ itemSize: 100 }"
                tableStyle="min-width: 50rem"
              >
                <Column v-for="col of columnsTableArrayOfArray[i-1]" :key="col.field" :field="col.field" :header="col.header" sortable style="width: 10%">
                  <template #body="slotProps">
                    <div :class="statusClass(slotProps.index, slotProps.field)">
                      {{ slotProps.data[slotProps.field] }}
                    </div>
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </template>
      </div>
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style></style>
