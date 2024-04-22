<script>
import { FilterMatchMode } from 'primevue/api'
import Multiselect from '@vueform/multiselect'
import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import { getKKSFilterByMasks, getTypesOfSensors, getSignals, cancelSignals, getKKSByMasksForTable } from '../stores'

import { useApplicationStore } from '../stores/applicationStore'

export default {
  name: 'SignalsReport',
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

    const qualitiesName = ref([
      '8 - (BNC) - ОТКАЗ СВЯЗИ (TIMEOUT)',
      '16 - (BSF) - ОТКАЗ ПАРАМ',
      '24 - (BCF) - ОТКАЗ СВЯЗИ',
      '28 - (BOS) - ОТКАЗ ОБСЛУЖ',
      '88 - (BLC) - ОТКАЗ РАСЧЕТ',
      '192 - (GOD) – ХОРОШ',
      '200 - (GLC) - ХОРОШ РАСЧЕТ',
      '216 - (GFO) - ХОРОШ ИМИТИР',
      '224 - (GLT) - ХОРОШ ЛОКАЛ ВРЕМ'
    ])
    const quality = ref(null)
    let chosenQuality = []

    const dateTime = ref()
    const dateDeepOfSearch = ref()
    const maxDateTime = ref(new Date())
    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const dataTable = ref()
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    const filters = ref(null)

    const progressBarSignals = ref('0')
    const progressBarSignalsActive = ref(false)

    const statusRequestTextArea = ref('')
    const statusRequestCol = computed(() => {
      return props.collapsedSidebar ? 115 : 90
    })

    let delayTimer = null

    const estimatedTime = ref(0.0)
    const chosenSensors = ref([])

    const dialogBigRequestActive = ref(false)
    const scrolledTagBigRequestTextArea = ref('')

    const interruptDisabledFlag = ref(false)

    onMounted(async () => {
      await getTypesOfSensors(typesOfSensorsDataOptions)
      // disabledSensorsAndTemplate.value = true
      // await getKKSFilterByMasks(sensorsAndTemplateOptions, chosenTypesOfSensorsData, chosenSensorsAndTemplate)
      // disabledSensorsAndTemplate.value = false
      window.addEventListener('beforeunload', async (event) => {
        // await context.emit('toggleButtonDialogConfigurator', false)
        await cancelSignals()
      })
    })

    onBeforeUnmount(async () => {
      window.removeEventListener('beforeunload', async (event) => {})
    })

    onUnmounted(async () => {
      if (progressBarSignalsActive.value)
        await context.emit('toggleButtonDialogConfigurator', false)
      await cancelSignals()
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
      if (sensorsAndTemplateOptions.value[0].options.includes(query['value'])) return
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

    function onMultiselectQualitiesChange(val) {
      chosenQuality = val
    }

    function onDateDeepOfSearchClick() {
      maxDateTime.value = new Date()
    }

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      if (
        !chosenTypesOfSensorsData.length ||
        !chosenSensorsAndTemplate.length ||
        !chosenQuality.length ||
        !dateTime.value ||
        !dateDeepOfSearch.value
      ) {
        alert('Не заполнены параметры запроса!')
        return
      }

      if (dateTime.value <= dateDeepOfSearch.value) {
        alert('Глубина поиска в архивах не должна превышать указанную дату запроса')
        return
      }

      if (progressBarSignalsActive.value) return
      dateTimeBeginReport.value = new Date().toLocaleString()

      await context.emit('toggleButtonDialogConfigurator', true)
      dataTableStartRequested.value = true
      progressBarSignalsActive.value = true
      progressBarSignals.value = '0'
      statusRequestTextArea.value = ''
      statusRequestTextArea.value +=
        'Начало выполнения запроса...\nОценка времени выполнения запроса...\n'

      interruptDisabledFlag.value = true

      chosenSensors.value = []
      await getKKSByMasksForTable(chosenSensors, chosenTypesOfSensorsData, chosenSensorsAndTemplate)

      estimatedTime.value =
        (chosenSensors.value.length * chosenQuality.length) /
        applicationStore.estimatedSliceRateInHours

      // Если расчетное время больше предельного, то выдаем пользователю диалоговое окно с подтверждением запроса
      if (estimatedTime.value >= applicationStore.sliceTimeLimitInHours) {
        scrolledTagBigRequestTextArea.value = ''
        scrolledTagBigRequestTextArea.value = sensorsAndTemplateOptions.value[1].options.join('\n')
        dialogBigRequestActive.value = true
        return
      }

      filters.value = {
        'Код сигнала (KKS)': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        'Дата и время измерения': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        Значение: {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        Качество: {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        'Код качества': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        }
      }

      interruptDisabledFlag.value = false

      await getSignals(
        chosenTypesOfSensorsData,
        chosenSensorsAndTemplate,
        chosenQuality,
        dateTime.value,
        dateDeepOfSearch.value,
        dataTable,
        dataTableRequested
      )
      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarSignals.value = '100'
      progressBarSignalsActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)
    }

    async function onInterruptRequestButtonClick() {
      if (progressBarSignalsActive.value)
        await context.emit('toggleButtonDialogConfigurator', false)
      cancelSignals()
      dataTableStartRequested.value = false
      progressBarSignalsActive.value = false
    }

    function qualityClass(quality) {
      return [
        {
          'text-danger': applicationStore.badCode.includes(quality['Качество']),
          'text-warning': quality['Качество'] === '' || quality['Качество'] === 'NaN'
        }
      ]
    }

    function codeOfQualityClass(code) {
      return [
        {
          'text-danger': applicationStore.badNumericCode.includes(code['Код качества']),
          'text-warning': code['Код качества'] === '' || code['Код качества'] === 'NaN'
        }
      ]
    }

    function setProgressBarSignals(count) {
      progressBarSignals.value = String(count)
    }
    window.eel.expose(setProgressBarSignals, 'setProgressBarSignals')

    function setUpdateSignalsRequestStatus(statusString) {
      statusRequestTextArea.value += String(statusString)
      let textarea = document.getElementById('signals-request-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateSignalsRequestStatus, 'setUpdateSignalsRequestStatus')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathSignalsCsv = 'signals_slice.csv'
      link.setAttribute('download', pathSignalsCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'signals_slice.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      const link = document.createElement('a')
      const pathSignalsReport = 'report/signals_slice.pdf'
      link.setAttribute('download', pathSignalsReport)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'report/signals_slice.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonRemoveOptionClick(option) {
      let index = sensorsAndTemplateOptions.value[0].options.indexOf(option)
      if (index >= 0) {
        sensorsAndTemplateOptions.value[0].options.splice(index, 1)
      }
    }

    async function onButtonCancelBigRequestClick() {
      dialogBigRequestActive.value = false
      progressBarSignals.value = '100'
      progressBarSignalsActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)
    }

    async function onBigRequestButtonClick() {
      dialogBigRequestActive.value = false

      statusRequestTextArea.value +=
        'Подготовка к выполнению долгого запроса\n'

      filters.value = {
        'Код сигнала (KKS)': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        'Дата и время измерения': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        Значение: {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        Качество: {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        'Код качества': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        }
      }

      interruptDisabledFlag.value = false

      await getSignals(
        chosenTypesOfSensorsData,
        chosenSensorsAndTemplate,
        chosenQuality,
        dateTime.value,
        dateDeepOfSearch.value,
        dataTable,
        dataTableRequested
      )
      dateTimeEndReport.value = new Date().toLocaleString()
      progressBarSignals.value = '100'
      progressBarSignalsActive.value = false
      await context.emit('toggleButtonDialogConfigurator', false)
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
      qualitiesName,
      quality,
      chosenQuality,
      onMultiselectQualitiesChange,
      dateTime,
      maxDateTime,
      dateDeepOfSearch,
      onDateDeepOfSearchClick,
      dateTimeBeginReport,
      dateTimeEndReport,
      onRequestButtonClick,
      onInterruptRequestButtonClick,
      interruptDisabledFlag,
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
      filters,
      qualityClass,
      codeOfQualityClass,
      progressBarSignals,
      progressBarSignalsActive,
      statusRequestTextArea,
      statusRequestCol,
      setUpdateSignalsRequestStatus,
      setProgressBarSignals,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick,
      onButtonRemoveOptionClick,
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
    <h1 align="center">Срезы сигналов</h1>
    <div class="container">
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="typesOfSensorsDataSignalsReport">Выберите тип данных тегов</label>
          <Multiselect
            id="typesOfSensorsDataSignalsReport"
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
          <label for="sensorsAndTemplateSignalsReport"
            >Выберите шаблон или теги сигналов, проходящие по условию введенного шаблона</label
          >
          <Multiselect
            id="sensorsAndTemplateSignalsReport"
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
        <div class="col" style="padding-bottom: 20px">
          <label for="qualitySignalsReport">Код качества сигнала</label>
          <Multiselect
            id="qualitySignalsReport"
            v-model="quality"
            mode="tags"
            :close-on-select="false"
            :searchable="true"
            :create-option="false"
            :options="qualitiesName"
            placeholder="Выберите код качества сигнала"
            limit="-1"
            @change="onMultiselectQualitiesChange"
          ></Multiselect>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="calendarDateDeepOfSearchSignalsReport">Глубина поиска в архивах</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <Calendar
            id="calendarDateDeepOfSearchSignalsReport"
            v-model="dateDeepOfSearch"
            :maxDate="maxDateTime"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
            @click="onDateDeepOfSearchClick"
          ></Calendar>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <label for="calendarDateSignalsReport">Введите дату</label>
        </div>
      </div>
      <div class="row">
        <div class="col">
          <Calendar
            id="calendarDateSignalsReport"
            v-model="dateTime"
            show-time
            hour-format="24"
            show-seconds="true"
            placeholder="ДД/ММ/ГГ ЧЧ:ММ:СС"
            manualInput="false"
            date-format="dd/mm/yy"
            show-icon
            show-button-bar
          ></Calendar>
        </div>
        <div class="col">
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
      <div class="row" v-if="progressBarSignalsActive">
        <div class="col-10 align-self-center">
          <ProgressBar :value="progressBarSignals"></ProgressBar>
        </div>
        <div class="col-2">
          <Button @click="onInterruptRequestButtonClick" :disabled="interruptDisabledFlag">Прервать запрос</Button>
        </div>
      </div>
      <div class="row" v-if="progressBarSignalsActive">
        <div class="col">
          <TextArea
            id="signals-request-text-area"
            v-model="statusRequestTextArea"
            rows="10"
            :cols="statusRequestCol"
            readonly
            :style="{ resize: 'none', 'overflow-y': scroll, width: '83%' }"
            >{{ statusRequestTextArea }}</TextArea
          >
        </div>
      </div>
      <div class="row">
        <div class="card" v-if="dataTableRequested">
          <DataTable
            v-model:filters="filters"
            :value="dataTable"
            paginator
            :rows="10"
            :rowsPerPageOptions="[10, 20, 50, 100]"
            scrollable="true"
            scrollHeight="1000px"
            columnResizeMode="fit"
            showGridlines="true"
            tableStyle="min-width: 50rem"
            dataKey="Код сигнала (KKS)"
            filterDisplay="row"
          >
            <Column
              field="Код сигнала (KKS)"
              header="Код сигнала (KKS)"
              sortable
              style="width: 35%"
            >
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
            </Column>
            <Column
              field="Дата и время измерения"
              header="Дата и время измерения"
              sortable
              style="width: 30%"
            >
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
            </Column>
            <Column field="Значение" header="Значение" sortable style="width: 10%">
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
            </Column>
            <Column field="Качество" header="Качество" sortable style="width: 20%">
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
              <template #body="slotProps">
                <div :class="qualityClass(slotProps.data)">
                  {{ slotProps.data['Качество'] }}
                </div>
              </template>
            </Column>
            <Column field="Код качества" header="Код качества" sortable style="width: 5%">
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
              <template #body="slotProps">
                <div :class="codeOfQualityClass(slotProps.data)">
                  {{ slotProps.data['Код качества'] }}
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>
