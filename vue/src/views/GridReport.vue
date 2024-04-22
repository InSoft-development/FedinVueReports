<script>
import { FilterMatchMode } from 'primevue/api'
import Multiselect from '@vueform/multiselect'

import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import {
  getKKSFilterByMasks,
  getTypesOfSensors,
  getKKSByMasksForTable,
  getGrid,
  cancelGrid
} from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'GridReport',
  components: { Multiselect },
  props: {
    collapsedSidebar: Boolean
  },
  emits: ['toggleButtonDialogConfigurator'],
  setup(props, context) {
    const applicationStore = useApplicationStore()

    const typesOfSensorsDataValue = ref(null)
    const typesOfSensorsDataOptions = ref([
      {
        label: 'Выбрать все типы данных',
        options: []
      }
    ])
    let chosenTypesOfSensorsData = []

    const sensorsAndTemplateValue = ref([])
    const sensorsAndTemplateOptions = ref([
      {
        label: 'Шаблоны',
        options: [
          'Sochi2\\.GT\\.AM\\.\\S*-AM\\.Q?$',
          '.*\\.state\\..*',
          '.*-icCV_.*\\.state\\..*',
          'Sochi2\\.GT\\.AM\\..*',
          'Sochi2\\..*',
          'Unit2\\..*'
        ]
      },
      {
        label: 'Теги KKS сигналов',
        options: []
      }
    ])
    let chosenSensorsAndTemplate = []
    const disabledSensorsAndTemplate = ref(true)
    const isLoadingSensorsAndTemplate = ref(false)

    const dateTimeBegin = ref()
    const dateTimeEnd = ref()

    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const progressBarGrid = ref('0')
    const progressBarGridActive = ref(false)

    const statusRequestTextArea = ref('')
    const statusRequestCol = computed(() => {
      return props.collapsedSidebar ? 115 : 90
    })

    const dataCodeTable = ref()
    const dataTable = ref()
    const dataTableStatus = ref()
    const columnsTable = ref([])
    const countOfDataTable = ref(0)
    const columnsTableArrayOfArray = ref([])
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    const filters = ref(null)

    let delayTimer = null

    const estimatedTime = ref(0.0)
    const chosenSensors = ref([])

    const dialogBigRequestActive = ref(false)
    const scrolledTagBigRequestTextArea = ref('')

    const interruptDisabledFlag = ref(false)

    onMounted(async () => {
      await getTypesOfSensors(typesOfSensorsDataOptions)

      window.addEventListener('beforeunload', async (event) => {
        // await context.emit('toggleButtonDialogConfigurator')
        await cancelGrid()
      })
    })

    onBeforeUnmount(async () => {
      window.removeEventListener('beforeunload', async (event) => {})
      let verticalScroll = document.getElementById('data-table')
      verticalScroll = verticalScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      verticalScroll.removeEventListener('scroll', synchroScroll)
    })

    onUnmounted(async () => {
      if (progressBarGridActive.value) await context.emit('toggleButtonDialogConfigurator', false)
      await cancelGrid()
      let verticalScroll = document.getElementById('data-table')
      verticalScroll = verticalScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      verticalScroll.removeEventListener('scroll', synchroScroll)
    })

    async function onTypesOfSensorsDataChange(val) {
      chosenTypesOfSensorsData = val
      if (!chosenTypesOfSensorsData.length) {
        disabledSensorsAndTemplate.value = true
      } else {
        disabledSensorsAndTemplate.value = true
        isLoadingSensorsAndTemplate.value = true
        await getKKSFilterByMasks(
          sensorsAndTemplateOptions,
          chosenTypesOfSensorsData,
          chosenSensorsAndTemplate
        )
        isLoadingSensorsAndTemplate.value = false
        disabledSensorsAndTemplate.value = false
      }
    }

    async function onMultiselectSensorsAndTemplateChange(val) {
      if (
        window.event.target.id.includes('divRemoveButton') ||
        window.event.target.id.includes('removeButton') ||
        window.event.target.id.includes('spanRemoveButton')
      ) {
        let lastVal = val[val.length - 1]
        await onButtonRemoveOptionClick(lastVal)
        await sensorsAndTemplateValue.value.pop()
        return
      }

      disabledSensorsAndTemplate.value = true
      isLoadingSensorsAndTemplate.value = true
      chosenSensorsAndTemplate = val
      await getKKSFilterByMasks(
        sensorsAndTemplateOptions,
        chosenTypesOfSensorsData,
        chosenSensorsAndTemplate
      )
      isLoadingSensorsAndTemplate.value = false
      disabledSensorsAndTemplate.value = false
    }

    function onMultiselectSensorsAndTemplateCreateTag(query) {
      sensorsAndTemplateOptions.value[0].options.push(query['value'])
      sensorsAndTemplateValue.value.push(query['value'])
    }

    async function onMultiselectSensorsAndTemplateSearchChange(query) {
      // Последовательная фильтрация по регуляркам
      clearTimeout(delayTimer)
      delayTimer = setTimeout(async function () {
        isLoadingSensorsAndTemplate.value = true
        let chosenFilterSensorsAndTemplate = chosenSensorsAndTemplate.slice()
        chosenFilterSensorsAndTemplate.push(String(query))
        await getKKSFilterByMasks(
          sensorsAndTemplateOptions,
          chosenTypesOfSensorsData,
          chosenFilterSensorsAndTemplate
        )
        isLoadingSensorsAndTemplate.value = false
      }, 1000)
      // Можно заменить на фильтр только по вводимой регулярке
      // await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenTypesOfSensorsData, query)
    }

    async function onMultiselectSensorsAndTemplateSelect(val, option) {
      return
    }

    async function onMultiselectSensorsAndTemplateDeselect(val, option) {
      return
    }

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      if (
        !chosenTypesOfSensorsData.length ||
        !chosenSensorsAndTemplate.length ||
        !dateTimeBegin.value ||
        !dateTimeEnd.value
      ) {
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
      if (progressBarGridActive.value) return
      dateTimeBeginReport.value = new Date().toLocaleString()
      await context.emit('toggleButtonDialogConfigurator', true)

      dataTableStartRequested.value = true

      progressBarGridActive.value = true
      progressBarGrid.value = '0'

      statusRequestTextArea.value = ''
      statusRequestTextArea.value +=
        'Начало выполнения запроса...\nОценка времени выполнения запроса...\n'

      interruptDisabledFlag.value = true

      chosenSensors.value = []
      let differenceInTime = dateTimeEnd.value.getTime() - dateTimeBegin.value.getTime()
      let differenceInDimension = Math.round(
        differenceInTime / (1000 * applicationStore.deltaTimeInSeconds[intervalRadio.value])
      )

      await getKKSByMasksForTable(chosenSensors, chosenTypesOfSensorsData, chosenSensorsAndTemplate)

      estimatedTime.value =
        (chosenSensors.value.length * differenceInDimension) /
        (applicationStore.estimatedGridRateInHours * interval.value)

      // Если расчетное время больше предельного, то выдаем пользователю диалоговое окно с подтверждением запроса
      if (estimatedTime.value >= applicationStore.gridTimeLimitInHours) {
        scrolledTagBigRequestTextArea.value = ''
        scrolledTagBigRequestTextArea.value = sensorsAndTemplateOptions.value[1].options.join('\n')
        dialogBigRequestActive.value = true
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

      interruptDisabledFlag.value = false

      await getGrid(
        chosenSensors.value,
        dateTimeBegin.value,
        dateTimeEnd.value,
        interval.value,
        intervalRadio.value,
        dataTable,
        dataTableRequested,
        dataTableStatus
      )

      // countOfDataTable.value = Math.ceil(chosenSensors.value.length / 5)

      // if (countOfDataTable.value === 1) columnsTableArrayOfArray.value.push(columnsTableArray)
      // else {
      //   for (let i = 0; i < countOfDataTable.value; i++) {
      //     if (i === 0) columnsTableArrayOfArray.value.push(columnsTable.value.slice(0, 6))
      //     else {
      //       columnsTableArrayOfArray.value.push(columnsTable.value.slice(i * 5 + 1, i * 5 + 6))
      //       columnsTableArrayOfArray.value[i].unshift({
      //         field: 'Метка времени',
      //         header: 'Метка времени'
      //       })
      //     }
      //   }
      // }

      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarGrid.value = '100'
      progressBarGridActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)

      let verticalScroll = document.getElementById('data-table')
      verticalScroll = verticalScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      verticalScroll.addEventListener('scroll', synchroScroll, false)
    }

    function onInterruptRequestButtonClick() {
      if (progressBarGridActive.value) context.emit('toggleButtonDialogConfigurator', false)
      cancelGrid()
      dataTableStartRequested.value = false
      progressBarGridActive.value = false
    }

    function setProgressBarGrid(count) {
      progressBarGrid.value = String(count)
    }
    window.eel.expose(setProgressBarGrid, 'setProgressBarGrid')

    function setUpdateGridRequestStatus(statusString) {
      statusRequestTextArea.value += String(statusString)
      let textarea = document.getElementById('grid-request-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateGridRequestStatus, 'setUpdateGridRequestStatus')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathCodeCsv = 'code.csv'
      link.setAttribute('download', pathCodeCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'code.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()

      const pathGridCsv = 'grid.csv'
      link.setAttribute('download', pathGridCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'grid.csv')
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
          'text-danger': applicationStore.badCode.includes(
            dataTableStatus.value[index][String(field)]
          ),
          'text-warning':
            dataTableStatus.value[index][String(field)] === 'missed' ||
            dataTableStatus.value[index][String(field)] === 'NaN' ||
            dataTable.value[index][String(field)] === 'NaN'
        }
      ]
    }

    function onButtonRemoveOptionClick(option) {
      let index = sensorsAndTemplateOptions.value[0].options.indexOf(option)
      if (index >= 0) {
        sensorsAndTemplateOptions.value[0].options.splice(index, 1)
      }
    }

    const synchroScroll = (event) => {
      let codeScroll = document.getElementById('code-table')
      codeScroll = codeScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      let dataScroll = document.getElementById('data-table')
      dataScroll = dataScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      codeScroll.scrollTop = dataScroll.scrollLeft * 0.25
    }

    const synchroScrollByHref = (event) => {
      let codeScroll = document.getElementById('code-table')
      codeScroll = codeScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      let dataScroll = document.getElementById('data-table')
      dataScroll = dataScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      dataScroll.scrollLeft = codeScroll.scrollTop / 0.25
    }

    async function onButtonCancelBigRequestClick() {
      dialogBigRequestActive.value = false
      progressBarGrid.value = '100'
      progressBarGridActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)
    }

    async function onBigRequestButtonClick() {
      dialogBigRequestActive.value = false

      statusRequestTextArea.value +=
        'Подготовка к выполнению долгого запроса\n'

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

      interruptDisabledFlag.value = false

      await getGrid(
        chosenSensors.value,
        dateTimeBegin.value,
        dateTimeEnd.value,
        interval.value,
        intervalRadio.value,
        dataTable,
        dataTableRequested,
        dataTableStatus
      )

      // countOfDataTable.value = Math.ceil(chosenSensors.value.length / 5)
      //
      // if (countOfDataTable.value === 1) columnsTableArrayOfArray.value.push(columnsTableArray)
      // else {
      //   for (let i = 0; i < countOfDataTable.value; i++) {
      //     if (i === 0) columnsTableArrayOfArray.value.push(columnsTable.value.slice(0, 6))
      //     else {
      //       columnsTableArrayOfArray.value.push(columnsTable.value.slice(i * 5 + 1, i * 5 + 6))
      //       columnsTableArrayOfArray.value[i].unshift({
      //         field: 'Метка времени',
      //         header: 'Метка времени'
      //       })
      //     }
      //   }
      // }

      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarGrid.value = '100'
      progressBarGridActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)

      let verticalScroll = document.getElementById('data-table')
      verticalScroll = verticalScroll.querySelector('.p-virtualscroller.p-virtualscroller-inline')
      verticalScroll.addEventListener('scroll', synchroScroll, false)
    }

    return {
      typesOfSensorsDataValue,
      typesOfSensorsDataOptions,
      chosenTypesOfSensorsData,
      onTypesOfSensorsDataChange,
      sensorsAndTemplateValue,
      sensorsAndTemplateOptions,
      chosenSensorsAndTemplate,
      disabledSensorsAndTemplate,
      isLoadingSensorsAndTemplate,
      onMultiselectSensorsAndTemplateChange,
      onMultiselectSensorsAndTemplateCreateTag,
      onMultiselectSensorsAndTemplateSearchChange,
      onMultiselectSensorsAndTemplateSelect,
      onMultiselectSensorsAndTemplateDeselect,
      dateTimeBegin,
      dateTimeEnd,
      dateTimeBeginReport,
      dateTimeEndReport,
      interval,
      intervalRadio,
      progressBarGrid,
      progressBarGridActive,
      statusRequestTextArea,
      statusRequestCol,
      setUpdateGridRequestStatus,
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
      onInterruptRequestButtonClick,
      interruptDisabledFlag,
      setProgressBarGrid,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick,
      statusClass,
      onButtonRemoveOptionClick,
      synchroScroll,
      synchroScrollByHref,
      estimatedTime,
      chosenSensors,
      dialogBigRequestActive,
      scrolledTagBigRequestTextArea,
      onButtonCancelBigRequestClick,
      onBigRequestButtonClick
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Сетка сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="typesOfSensorsDataGridReport">Выберите тип данных тегов</label>
          <Multiselect
            id="typesOfSensorsDataGridReport"
            v-model="typesOfSensorsDataValue"
            mode="tags"
            :close-on-select="false"
            :groups="true"
            :options="typesOfSensorsDataOptions"
            :searchable="true"
            :create-option="false"
            placeholder="Выберите тип данных тегов"
            limit="-1"
            :can-clear="false"
            @change="onTypesOfSensorsDataChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="sensorsAndTemplateGridReport"
            >Выберите шаблон или теги сигналов, проходящие по условию введенного шаблона</label
          >
          <Multiselect
            id="sensorsAndTemplateGridReport"
            v-model="sensorsAndTemplateValue"
            mode="tags"
            :disabled="disabledSensorsAndTemplate"
            :close-on-select="false"
            :groups="true"
            :options="sensorsAndTemplateOptions"
            :searchable="true"
            :create-option="true"
            :filter-results="false"
            :loading="isLoadingSensorsAndTemplate"
            placeholder="Выберите шаблон или теги сигналов"
            limit="-1"
            appendNewOption="false"
            @change="onMultiselectSensorsAndTemplateChange"
            @create="onMultiselectSensorsAndTemplateCreateTag"
            @search-change="onMultiselectSensorsAndTemplateSearchChange"
            @select="onMultiselectSensorsAndTemplateSelect"
            @deselect="onMultiselectSensorsAndTemplateDeselect"
          >
            <template v-slot:option="{ option }">
              <div class="multiselect-options">
                <span class="multiselect-tag-wrapper">{{ option.label }}</span>
              </div>
              <div :id="'divRemoveButton' + option.label" style="margin: 0 0 0 auto">
                <Button
                  v-if="sensorsAndTemplateOptions[0].options.includes(option.label)"
                  :id="'removeButton' + option.label"
                  class="multiselect-tag-remove"
                >
                  <span
                    :id="'spanRemoveButton' + option.label"
                    class="multiselect-tag-remove-icon"
                  ></span>
                </Button>
              </div>
            </template>
          </Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="calendarDateBeginGridReport">Введите дату начала</label>
        </div>
        <div class="col">
          <label for="calendarDateEndGridReport">Введите дату конца</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <Calendar
            id="calendarDateBeginGridReport"
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
            id="calendarDateEndGridReport"
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
          <label for="intervalGridReport">Интервал</label>
        </div>
      </div>
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <InputNumber
            v-model="interval"
            id="intervalGridReport"
            input-id="interval"
            :useGrouping="false"
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
          <Button @click="onRequestButtonClick" :disabled="isLoadingSensorsAndTemplate"
            >Запрос</Button
          >
          <Dialog
            v-model="dialogBigRequestActive"
            :visible="dialogBigRequestActive"
            :closable="false"
            header="Подтверждение запуска длительного по времени запроса"
            position="center"
            :modal="true"
            :draggable="false"
            :style="{ width: '50rem' }"
          >
            <div class="container">
              <div class="row">
                <div class="col">
                  <b>Запрошенные теги</b>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <TextArea
                    id="big-request-text-area"
                    v-model="scrolledTagBigRequestTextArea"
                    rows="10"
                    cols="80"
                    readonly
                    :style="{ resize: 'none', 'overflow-y': scroll }"
                    >{{ scrolledTagBigRequestTextArea }}</TextArea
                  >
                </div>
              </div>
              <div class="row">
                <div class="col">
                  Примерная оценка времени выполнения запроса: <b>{{ estimatedTime }} чаc.</b>
                </div>
              </div>
            </div>
            <template #footer>
              <Button
                label="Отмена"
                icon="pi pi-times"
                @click="onButtonCancelBigRequestClick"
                text
              />
              <Button
                label="Запустить запрос"
                icon="pi pi-check"
                @click="onBigRequestButtonClick"
              />
            </template>
          </Dialog>
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
      <div class="row" v-if="progressBarGridActive">
        <div class="col-10 align-self-center">
          <ProgressBar :value="progressBarGrid"></ProgressBar>
        </div>
        <div class="col-2">
          <Button @click="onInterruptRequestButtonClick" :disabled="interruptDisabledFlag">Прервать запрос</Button>
        </div>
      </div>
      <div class="row" v-if="progressBarGridActive">
        <div class="col">
          <TextArea
            id="grid-request-text-area"
            v-model="statusRequestTextArea"
            rows="10"
            :cols="statusRequestCol"
            readonly
            :style="{ resize: 'none', 'overflow-y': scroll, width: '83%' }"
            >{{ statusRequestTextArea }}</TextArea
          >
        </div>
      </div>
      <div class="row" style="padding-bottom: 20px">
        <div style="padding-bottom: 20px">
          <div class="card" v-if="dataTableRequested" id="code-table">
            <DataTable
              :value="dataCodeTable"
              scrollable="true"
              scrollHeight="400px"
              columnResizeMode="fit"
              showGridlines="true"
              :virtualScrollerOptions="{ itemSize: 50 }"
              tableStyle="min-width: 50rem"
            >
              <Column field="№" header="№" sortable style="width: 50%"> </Column>
              <Column
                field="Обозначение сигнала"
                header="Обозначение сигнала"
                sortable
                style="width: 50%"
              >
                <template #body="slotProps">
                  <a :href="'#' + slotProps.data['№']" @click="synchroScrollByHref">
                    <div>
                      {{ slotProps.data[slotProps.field] }}
                    </div>
                  </a>
                </template>
              </Column>
            </DataTable>
          </div>
          <div class="card" v-if="dataTableRequested" id="data-table">
            <DataTable
              v-model:filters="filters"
              :value="dataTable"
              scrollable="true"
              scrollHeight="1000px"
              columnResizeMode="fit"
              showGridlines="true"
              :virtualScrollerOptions="{ itemSize: 50 }"
              tableStyle="min-width: 50rem"
              dataKey="Метка времени"
              filterDisplay="row"
            >
              <Column
                v-for="col of columnsTable"
                :key="col.field"
                :field="col.field"
                :header="col.header"
                sortable
                v-bind:frozen="[col.field === 'Метка времени']"
                v-bind:style="[
                  col.field === 'Метка времени'
                    ? { 'min-width': '300px' }
                    : { 'min-width': '200px' }
                ]"
              >
                <template #body="slotProps">
                  <div :class="statusClass(slotProps.index, slotProps.field)">
                    {{ slotProps.data[slotProps.field] }}
                  </div>
                </template>
                <template #filter="{ filterModel, filterCallback }">
                  <InputText
                    :id="col.header"
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
      </div>
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style></style>
