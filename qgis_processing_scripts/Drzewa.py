"""
Model exported as python.
Name : Drzewa
Group : 
With QGIS : 32807
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class Drzewa(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('poligony_koron_drzew', 'Poligony koron drzew', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSource('warstwa_maski', 'Warstwa maski', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('nmt', 'NMT', defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Drzewa', 'Drzewa', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(9, model_feedback)
        results = {}
        outputs = {}

        # Zaznacz drzewa w obrębie miasta
        alg_params = {
            'INPUT': parameters['poligony_koron_drzew'],
            'INTERSECT': parameters['warstwa_maski'],
            'METHOD': 0,  # utworzenie nowej selekcji
            'PREDICATE': [0],  # przecinają się
        }
        outputs['ZaznaczDrzewaWObrbieMiasta'] = processing.run('native:selectbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Zaznacz drzewa o koronie większej niż 3m2
        alg_params = {
            'FIELD': 'cnvhll_',
            'INPUT': parameters['poligony_koron_drzew'],
            'METHOD': 2,  # usunięcie z bieżącej selekcji
            'OPERATOR': 4,  # <
            'VALUE': '3'
        }
        outputs['ZaznaczDrzewaOKoronieWikszejNi3m2'] = processing.run('qgis:selectbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Wyodrębnij tylko drzewa w mieście
        alg_params = {
            'INPUT': parameters['poligony_koron_drzew'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WyodrbnijTylkoDrzewaWMiecie'] = processing.run('native:saveselectedfeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Centroidy
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['WyodrbnijTylkoDrzewaWMiecie']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroidy'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Próbkuj wartości rastra
        alg_params = {
            'COLUMN_PREFIX': 'NMT_Z',
            'INPUT': outputs['Centroidy']['OUTPUT'],
            'RASTERCOPY': parameters['nmt'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PrbkujWartociRastra'] = processing.run('native:rastersampling', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Oblicz wysokość drzewa
        alg_params = {
            'FIELD_LENGTH': 4,
            'FIELD_NAME': 'h',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer (32 bit)
            'FORMULA': '"Z" - "NMT_Z1"',
            'INPUT': outputs['PrbkujWartociRastra']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ObliczWysokoDrzewa'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Zmień nazwę pola
        alg_params = {
            'FIELD': 'cnvhll_',
            'INPUT': outputs['ObliczWysokoDrzewa']['OUTPUT'],
            'NEW_NAME': 'area_m2',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZmieNazwPola'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Zmień nazwę pola
        alg_params = {
            'FIELD': 'NMT_Z1',
            'INPUT': outputs['ZmieNazwPola']['OUTPUT'],
            'NEW_NAME': 'h_asl',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ZmieNazwPola'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Usuń pola
        alg_params = {
            'COLUMN': ['Z'],
            'INPUT': outputs['ZmieNazwPola']['OUTPUT'],
            'OUTPUT': parameters['Drzewa']
        }
        outputs['UsuPola'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Drzewa'] = outputs['UsuPola']['OUTPUT']
        return results

    def name(self):
        return 'Drzewa'

    def displayName(self):
        return 'Drzewa'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Drzewa()
