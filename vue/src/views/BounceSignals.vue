<script>
import { FilterMatchMode } from 'primevue/api'
import Multiselect from '@vueform/multiselect'

import { ref, onMounted, onUnmounted, onBeforeUnmount, computed } from 'vue'
import {
  getKKSFilterByMasks,
  getTypesOfSensors,
  getKKSByMasksForTable,
  getBounceSignals,
  cancelBounce
} from '../stores'

export default {
  name: 'BounceSignals',
  components: { Multiselect },
  props: {
    collapsedSidebar: Boolean
  },
  emits: ['toggleButtonDialogConfigurator'],
  setup(props, context) {
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

    const dateTime = ref()
    const disableTime = ref(false)

    const dateTimeBeginReport = ref()
    const dateTimeEndReport = ref()

    const interval = ref(5)
    const intervalRadio = ref('minute')

    const progressBarBounceSignals = ref('0')
    const progressBarBounceSignalsActive = ref(false)

    const statusRequestTextArea = ref('')
    const statusRequestCol = computed(() => {
      return props.collapsedSidebar ? 115 : 90
    })

    const countShowSensors = ref(10)

    const currentDateChecked = ref(false)

    const dataTable = ref()
    const dataTableRequested = ref(false)
    const dataTableStartRequested = ref(false)

    const filters = ref(null)

    let delayTimer = null

    onMounted(async () => {
      await getTypesOfSensors(typesOfSensorsDataOptions)

      window.addEventListener('beforeunload', async (event) => {
        await context.emit('toggleButtonDialogConfigurator')
        await cancelBounce()
      })
    })

    onBeforeUnmount(async () => {
      window.removeEventListener('beforeunload', async (event) => {})
    })

    onUnmounted(async () => {
      if (progressBarBounceSignalsActive.value) await context.emit('toggleButtonDialogConfigurator')
      await cancelBounce()
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
      console.log('onMultiselectSensorsAndTemplateChange')

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

    async function onRequestButtonClick() {
      dataTableRequested.value = false
      dateTimeBeginReport.value = new Date().toLocaleString()

      if (
        !chosenTypesOfSensorsData.length ||
        !chosenSensorsAndTemplate.length ||
        !dateTime.value
      ) {
        alert('Не заполнены параметры запроса!')
        return
      }

      if (progressBarBounceSignalsActive.value) return
      await context.emit('toggleButtonDialogConfigurator')

      dataTableStartRequested.value = true

      progressBarBounceSignalsActive.value = true
      progressBarBounceSignals.value = '0'

      statusRequestTextArea.value = ''
      statusRequestTextArea.value += 'Начало выполнения запроса...\n'

      filters.value = {
        'Наименование датчика': {
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        },
        'Частота':{
          value: null,
          matchMode: FilterMatchMode.STARTS_WITH
        }
      }

      let chosenSensors = ref([])
      await getKKSByMasksForTable(chosenSensors, chosenTypesOfSensorsData, chosenSensorsAndTemplate)
      console.log(chosenSensors.value)

      await getBounceSignals(
        chosenSensors.value,
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
      await context.emit('toggleButtonDialogConfigurator')
    }

    function onInterruptRequestButtonClick() {
      if (progressBarBounceSignalsActive.value) context.emit('toggleButtonDialogConfigurator')
      cancelBounce()
      dataTableStartRequested.value = false
      progressBarBounceSignalsActive.value = false
    }

    function onChangeCheckbox() {
      if (!disableTime.value) dateTime.value = new Date()
      disableTime.value = !disableTime.value
    }

    function setProgressBarBounceSignals(count) {
      progressBarBounceSignals.value = String(count)
    }
    window.eel.expose(setProgressBarBounceSignals, 'setProgressBarBounceSignals')

    function setUpdateBounceRequestStatus(statusString) {
      statusRequestTextArea.value += String(statusString)
      let textarea = document.getElementById('bounce-request-text-area')
      textarea.scrollTop = textarea.scrollHeight
    }
    window.eel.expose(setUpdateBounceRequestStatus, 'setUpdateBounceRequestStatus')

    function onButtonDownloadCsvClick() {
      const link = document.createElement('a')
      const pathBounceCsv = 'bounce.csv'
      link.setAttribute('download', pathBounceCsv)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'bounce.csv')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonDownloadPdfClick() {
      const link = document.createElement('a')
      const pathBounceReport = 'report/bounce.pdf'
      link.setAttribute('download', pathBounceReport)
      link.setAttribute('type', 'application/octet-stream')
      link.setAttribute('href', 'report/bounce.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
    }

    function onButtonRemoveOptionClick(option) {
      let index = sensorsAndTemplateOptions.value[0].options.indexOf(option)
      if (index >= 0) {
        sensorsAndTemplateOptions.value[0].options.splice(index, 1)
      }
      console.log(sensorsAndTemplateOptions.value[0].options)
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
      dateTime,
      disableTime,
      dateTimeBeginReport,
      dateTimeEndReport,
      interval,
      intervalRadio,
      progressBarBounceSignals,
      progressBarBounceSignalsActive,
      statusRequestTextArea,
      statusRequestCol,
      countShowSensors,
      currentDateChecked,
      setUpdateBounceRequestStatus,
      dataTable,
      dataTableRequested,
      dataTableStartRequested,
      filters,
      onRequestButtonClick,
      onInterruptRequestButtonClick,
      setProgressBarBounceSignals,
      onChangeCheckbox,
      onButtonDownloadCsvClick,
      onButtonDownloadPdfClick,
      onButtonRemoveOptionClick
    }
  }
}
</script>

<template>
  <div>
    <h1 align="center">Дребезг сигналов</h1>
    <div class="container">
      <div class="col" style="padding-bottom: 20px">
        <label for="typesOfSensorsDataBounceReport">Выберите тип данных тегов</label>
        <Multiselect
          id="typesOfSensorsDataBounceReport"
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
      <div class="row">
        <div class="col" style="padding-bottom: 20px">
          <label for="sensorsAndTemplateBounceReport"
            >Выберите шаблон или теги сигналов, проходящие по условию введенного шаблона</label
          >
          <Multiselect
            id="sensorsAndTemplateBounceReport"
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
      <div class="row" v-if="progressBarBounceSignalsActive">
        <div class="col-10 align-self-center">
          <ProgressBar :value="progressBarBounceSignals"></ProgressBar>
        </div>
        <div class="col-2">
          <Button @click="onInterruptRequestButtonClick">Прервать запрос</Button>
        </div>
      </div>
      <div class="row" v-if="progressBarBounceSignalsActive">
        <div class="col">
          <TextArea
            id="bounce-request-text-area"
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
        <div class="card" v-if="dataTableRequested">
          <DataTable
            v-model:filters="filters"
            :value="dataTable"
            scrollable="true"
            scrollHeight="1000px"
            columnResizeMode="fit"
            showGridlines="true"
            tableStyle="min-width: 50rem"
            dataKey="Наименование датчика"
            filterDisplay="row"
          >
            <Column field="Наименование датчика" header="Наименование датчика" sortable>
              <template #filter="{ filterModel, filterCallback }">
                <InputText
                  v-model="filterModel.value"
                  type="text"
                  @input="filterCallback()"
                  class="p-column-filter"
                />
              </template>
            </Column>
            <Column field="Частота" header="Частота" sortable>
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
      <div class="row" v-if="dataTableRequested">Отчет: {{ dateTimeEndReport }}</div>
    </div>
  </div>
</template>

<style></style>
