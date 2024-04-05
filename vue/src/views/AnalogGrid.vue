<script>
import { FilterMatchMode } from 'primevue/api'
import Multiselect from '@vueform/multiselect'

import { ref, onMounted } from 'vue'
import { getAnalogKKS, getAnalogGrid } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'AnalogGrid',
  components: { Multiselect },
  setup() {
    const applicationStore = useApplicationStore()

    const analogSensors = ref([])
    const sensors = ref(null)
    const chosenSensors = ref([])

    const dateTimeBegin = ref()
    const dateTimeEnd = ref()

    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const progressBarAnalogSignals = ref('0')
    const progressBarAnalogSignalsActive = ref(false)

    const dataCodeTable = ref()
    const dataTable = ref()
    const dataTableStatus = ref()
    const columnsTable = ref([])
    const countOfDataTable = ref(0)
    const columnsTableArrayOfArray = ref([])
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    const filters = ref(null)

    onMounted(async () => {
      await getAnalogKKS(analogSensors)
    })

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

      filters.value = {
        'Метка времени': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        }
      }
      let codeTableArray = Array()
      let columnsTableArray = [{ field: 'Метка времени', header: 'Метка времени' }]

      for (const [index, element] of chosenSensors.value.entries()) {
        codeTableArray.push({ '№': index, 'Обозначение сигнала': element })
        columnsTableArray.push({ field: String(index), header: String(index) })
        filters.value[index] = { value: null, matchMode: FilterMatchMode.STARTS_WITH }
      }

      dataCodeTable.value = codeTableArray
      columnsTable.value = columnsTableArray

      progressBarAnalogSignalsActive.value = true
      progressBarAnalogSignals.value = '0'
      await getAnalogGrid(
        chosenSensors.value,
        dateTimeBegin.value,
        dateTimeEnd.value,
        interval.value,
        intervalRadio.value,
        dataTable,
        dataTableRequested,
        dataTableStatus
      )

      // countOfDataTable.value = Math.ceil(chosenSensors.value.length / 10)
      countOfDataTable.value = Math.ceil(chosenSensors.value.length / 5)

      if (countOfDataTable.value === 1) columnsTableArrayOfArray.value.push(columnsTableArray)
      else {
        for (let i = 0; i < countOfDataTable.value; i++) {
          // if (i === 0) columnsTableArrayOfArray.value.push(columnsTable.value.slice(0, 11))
          if (i === 0) columnsTableArrayOfArray.value.push(columnsTable.value.slice(0, 6))
          else {
            // columnsTableArrayOfArray.value.push(columnsTable.value.slice(i * 10 + 1, i * 10 + 11))
            columnsTableArrayOfArray.value.push(columnsTable.value.slice(i * 5 + 1, i * 5 + 6))
            columnsTableArrayOfArray.value[i].unshift({
              field: 'Метка времени',
              header: 'Метка времени'
            })
          }
        }
      }

      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarAnalogSignals.value = '100'
      progressBarAnalogSignalsActive.value = false
    }

    function setProgressBarAnalogSignals(count) {
      progressBarAnalogSignals.value = String(count)
    }
    window.eel.expose(setProgressBarAnalogSignals, 'setProgressBarAnalogSignals')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathAnalogGridCsv = 'analog_grid.csv'
      link.setAttribute('download', pathAnalogGridCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'analog_grid.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      const link = document.createElement('a')
      const pathSignalsReport = 'report/grid.zip'
      link.setAttribute('download', pathSignalsReport)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'report/grid.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function statusClass(index, field) {
      return [
        {
          'bg-danger text-white': applicationStore.badCode.includes(
            dataTableStatus.value[index][String(field)]
          ),
          'bg-warning text-white': dataTableStatus.value[index][String(field)] === 'missed'
        }
      ]
    }

    return {
      analogSensors,
      sensors,
      chosenSensors,
      onMultiselectSensorsChange,
      dateTimeBegin,
      dateTimeEnd,
      dateTimeBeginReport,
      dateTimeEndReport,
      interval,
      intervalRadio,
      progressBarAnalogSignals,
      progressBarAnalogSignalsActive,
      dataCodeTable,
      dataTable,
      dataTableStatus,
      columnsTable,
      countOfDataTable,
      columnsTableArrayOfArray,
      dataTableRequested,
      dataTableStartRequested,
      filters,
      onRequestButtonClick,
      setProgressBarAnalogSignals,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick,
      statusClass
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Сетка аналоговых сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="analogSensors">тег (KKS)</label>
          <Multiselect
            id="analogSensors"
            v-model="sensors"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="analogSensors"
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
      <div class="row" v-if="progressBarAnalogSignalsActive">
        <div class="col">
          <ProgressBar :value="progressBarAnalogSignals"></ProgressBar>
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
            <Column field="№" header="№" sortable style="width: 35%"></Column>
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
                v-model:filters="filters"
                :value="dataTable"
                scrollable="true"
                scrollHeight="1000px"
                columnResizeMode="fit"
                showGridlines="true"
                :virtualScrollerOptions="{ itemSize: 100 }"
                tableStyle="min-width: 50rem"
                dataKey="Метка времени"
                filterDisplay="row"
              >
                <Column
                  v-for="col of columnsTableArrayOfArray[i - 1]"
                  :key="col.field"
                  :field="col.field"
                  :header="col.header"
                  sortable
                  v-bind:style="[col.field === 'Метка времени' ? { width: '20%' } : null]"
                >
                  <template #body="slotProps">
                    <div :class="statusClass(slotProps.index, slotProps.field)">
                      {{ slotProps.data[slotProps.field] }}
                    </div>
                  </template>
                  <template #filter="{ filterModel, filterCallback }">
                    <InputText
                      v-model="filterModel.value"
                      type="text"
                      @input="filterCallback()"
                      class="p-column-filter"
                    />
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
