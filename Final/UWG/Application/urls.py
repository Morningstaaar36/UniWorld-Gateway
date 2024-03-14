from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    # Application
    path('', views.applicationHomeRenderer, name="applicationHomeRenderer"),
    path('createApplication/', views.createApplication, name="createApplication"),
    path('resumeApplication/', views.resumeApplication, name="resumeApplication"),
    path('deleteApplication/', views.deleteApplication, name="deleteApplication"),
    path('stopApplication/', views.stopApplication, name="stopApplication"),
    path('submitRenderer/', views.submitRenderer, name="submitRenderer"),
    path('finalSubmit/', views.finalSubmit, name="finalSubmit"),
    path('lastShowRenderer/',views.lastShowRenderer,name="lastShowRenderer"),
    # Program Selection
    path('addProgramSelectionRenderer/', views.addProgramSelectionRenderer, name="addProgramSelectionRenderer"),
    path('addProgramSelectionByLocationRenderer/', views.addProgramSelectionByLocationRenderer, name="addProgramSelectionByLocationRenderer"),
    path('addProgramSelectionByCriteriaRenderer/', views.addProgramSelectionByCriteriaRenderer, name="addProgramSelectionByCriteriaRenderer"),
    path('addProgramSelection/', views.addProgramSelection, name="addProgramSelection"),
    path('seeProgramSelection/', views.seeProgramSelection, name="seeProgramSelection"),
    path('deleteProgramSelection/', views.deleteProgramSelection, name="deleteProgramSelection"),
    path('submitSelection/', views.submitSelection, name="submitSelection"),
    # Personal Info
    path('addPersonalInfoRenderer/', views.addPersonalInfoRenderer, name="addPersonalInfoRenderer"),
    path('addPersonalInfo/', views.addPersonalInfo, name="addPersonalInfo"),
    path('seePersonalInfo/', views.seePersonalInfo, name="seePersonalInfo"),
    path('deletePersonalInfo/', views.deletePersonalInfo, name="deletePersonalInfo"),
    path('updatePersonalInfoRenderer/', views.updatePersonalInfoRenderer, name="updatePersonalInfoRenderer"),
    path('updatePersonalInfo/', views.updatePersonalInfo, name="updatePersonalInfo"),

   
    # Contact Info
    path('addContactInfoRenderer/', views.addContactInfoRenderer, name="addContactInfoRenderer"),
    path('addContactInfo/', views.addContactInfo, name="addContactInfo"),
    path('seeContactInfo/', views.seeContactInfo, name="seeContactInfo"),
    path('deleteContactInfo/', views.deleteContactInfo, name="deleteContactInfo"),
    path('updateContactInfoRenderer/', views.updateContactInfoRenderer, name="updateContactInfoRenderer"),
    path('updateContactInfo/', views.updateContactInfo, name="updateContactInfo"),

    # Citizenship Info
    path('addCitizenshipInfoRenderer/', views.addCitizenshipInfoRenderer, name="addCitizenshipInfoRenderer"),
    path('addCitizenshipInfo/', views.addCitizenshipInfo, name="addCitizenshipInfo"),
    path('seeCitizenshipInfo/', views.seeCitizenshipInfo, name="seeCitizenshipInfo"),
    path('deleteCitizenshipInfo/', views.deleteCitizenshipInfo, name="deleteCitizenshipInfo"),
    path('updateCitizenshipInfoRenderer/', views.updateCitizenshipInfoRenderer, name="updateCitizenshipInfoRenderer"),
    path('updateCitizenshipInfo/', views.updateCitizenshipInfo, name="updateCitizenshipInfo"),

    # Academic Record
    path('addAcademicRecordRenderer/', views.addAcademicRecordRenderer, name="addAcademicRecordRenderer"),
    path('addAcademicRecord/', views.addAcademicRecord, name="addAcademicRecord"),
    path('seeAcademicRecord/', views.seeAcademicRecord, name="seeAcademicRecord"),
    path('deleteAcademicRecord/', views.deleteAcademicRecord, name="deleteAcademicRecord"),
    path('updateAcademicRecordRenderer/', views.updateAcademicRecordRenderer, name="updateAcademicRecordRenderer"),
    path('updateAcademicRecord/', views.updateAcademicRecord, name="updateAcademicRecord"),
    path('AddOneMoreOrMove/',views.AddOneMoreOrMove,name="AddOneMoreOrMove"),
    # Portfolio
    path('addPortfolioRenderer/', views.addPortfolioRenderer, name="addPortfolioRenderer"),
    path('addPortfolio/', views.addPortfolio, name="addPortfolio"),
    path('seePortfolio/', views.seePortfolio, name="seePortfolio"),
    path('deletePortfolio/', views.deletePortfolio, name="deletePortfolio"),
    path('updatePortfolioRenderer/', views.updatePortfolioRenderer, name="updatePortfolioRenderer"),
    path('updatePortfolio/', views.updatePortfolio, name="updatePortfolio"),

    # Biological Info
    path('addBiologicalInfoRenderer/', views.addBiologicalInfoRenderer, name="addBiologicalInfoRenderer"),
    path('addBiologicalInfo/', views.addBiologicalInfo, name="addBiologicalInfo"),
    path('seeBiologicalInfo/', views.seeBiologicalInfo, name="seeBiologicalInfo"),
    path('deleteBiologicalInfo/', views.deleteBiologicalInfo, name="deleteBiologicalInfo"),
    path('updateBiologicalInfoRenderer/', views.updateBiologicalInfoRenderer, name="updateBiologicalInfoRenderer"),
    path('updateBiologicalInfo/', views.updateBiologicalInfo, name="updateBiologicalInfo"),

    # Address
    path('addAddressRenderer/', views.addAddressRenderer, name="addAddressRenderer"),
    path('addAddress/', views.addAddress, name="addAddress"),
    path('seeAddress/', views.seeAddress, name="seeAddress"),
    path('deleteAddress/', views.deleteAddress, name="deleteAddress"),
    path('updateAddressRenderer/', views.updateAddressRenderer, name="updateAddressRenderer"),
    path('updateAddress/', views.updateAddress, name="updateAddress"),
    # TOEFL
    path('addTOEFLRenderer/', views.addTOEFLRenderer, name="addTOEFLRenderer"),
    path('addTOEFL/', views.addTOEFL, name="addTOEFL"),
    path('seeTOEFL/', views.seeTOEFL, name="seeTOEFL"),
    path('deleteTOEFL/', views.deleteTOEFL, name="deleteTOEFL"),
    path('updateTOEFLRenderer/', views.updateTOEFLRenderer, name="updateTOEFLRenderer"),
    path('updateTOEFL/', views.updateTOEFL, name="updateTOEFL"),

    # IELTS
    path('addIELTSRenderer/', views.addIELTSRenderer, name="addIELTSRenderer"),
    path('addIELTS/', views.addIELTS, name="addIELTS"),
    path('seeIELTS/', views.seeIELTS, name="seeIELTS"),
    path('deleteIELTS/', views.deleteIELTS, name="deleteIELTS"),
    path('updateIELTSRenderer/', views.updateIELTSRenderer, name="updateIELTSRenderer"),
    path('updateIELTS/', views.updateIELTS, name="updateIELTS"),

    # GMAT
    path('addGMATRenderer/', views.addGMATRenderer, name="addGMATRenderer"),
    path('addGMAT/', views.addGMAT, name="addGMAT"),
    path('seeGMAT/', views.seeGMAT, name="seeGMAT"),
    path('deleteGMAT/', views.deleteGMAT, name="deleteGMAT"),
    path('updateGMATRenderer/', views.updateGMATRenderer, name="updateGMATRenderer"),
    path('updateGMAT/', views.updateGMAT, name="updateGMAT"),

    # GRE
    path('addGRERenderer/', views.addGRERenderer, name="addGRERenderer"),
    path('addGRE/', views.addGRE, name="addGRE"),
    path('seeGRE/', views.seeGRE, name="seeGRE"),
    path('deleteGRE/', views.deleteGRE, name="deleteGRE"),
    path('updateGRERenderer/', views.updateGRERenderer, name="updateGRERenderer"),
    path('updateGRE/', views.updateGRE, name="updateGRE"),

]
