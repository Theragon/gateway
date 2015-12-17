terminal_config = \
	{
		"guid": "b8c43cb0-df7a-11e4-807d-d77285f9547e",
		"tmsGuid": "b8c43cb1-df7a-11e4-807d-d77285f9547e",
		"serialNumber": "41852978",
		"terminalType": "MPED400",
		"softwareVersion": {
			"version": "1.0.0",
			"url": "https://pedserver.handpoint.com/binaries/eft-100.bin",
			"critical": False,
			"effectiveDate": "2013-09-07T12:07:19.011Z",
			"description": "desc1"
		},
		"configVersion": {
			"version": "4",
			"critical": False,
			"effectiveDate": "2013-09-07T12:07:19.027Z"
		},
		"cardAcceptors": [
			{
				"id": "TSYS",
				"name": "NAME",
				"locationName": "LOCATION",
				"addressLine1": "ADDRESS",
				"addressLine2": "ADDRESS_LINE_2",
				"city": "CITY",
				"zip": "200",
				"state": "st",
				"countryCodeAlpha2": "IS",
				"country": "ICELAND",
				"phone": "9999999999",
				"cardAcceptorTerminalConfig":
				{
					"acquirerTid": "TID",
					"timeZone": "GMT",
					"terminalLanguage": "en",
					"customFields": {
						"entry": [
							{
								"key": "hostCapturePosId",
								"value": "800018160066091"
							},
							{
								"key": "tsysAcquirerSolutionVersionId",
								"value": "H001"
							},
							{
								"key": "authenticationCode",
								"value": "WD03042015"
							},
							{
								"key": "tsysAcquirerSolutionDeveloperId",
								"value": "002628"
							}
						]
					}
				},
				"agreements": [
					{
						"agreementNumber": "360000000000012",
						"merchantCategoryCode": "4816",
						"protocol": "TSYS",
						"binList": [],
						"bins": [
							{
								"binId": "3",
								"luhnCheck": False,
								"expiryDateCheck": False,
								"saleAllowed": True,
								"refundAllowed": True,
								"serviceCodeCheck": False,
								"cardTypeId": "8000",
								"cardTypeName": "American Express Direct",
								"characteristic": "C",
								"customFields": {
									"entry": []
								}
							},
							{
								"binId": "6011",
								"luhnCheck": False,
								"expiryDateCheck": False,
								"saleAllowed": True,
								"refundAllowed": True,
								"serviceCodeCheck": False,
								"cardTypeId": "7000",
								"cardTypeName": "Discover Card",
								"characteristic": "C",
								"customFields": {
									"entry": []
								}
							},
							{
								"binId": "4",
								"luhnCheck": False,
								"expiryDateCheck": False,
								"saleAllowed": True,
								"refundAllowed": True,
								"serviceCodeCheck": False,
								"cardTypeId": "1000",
								"cardTypeName": "VISA",
								"characteristic": "C",
								"customFields": {
									"entry": []
								}
							},
							{
								"binId": "5",
								"luhnCheck": False,
								"expiryDateCheck": False,
								"saleAllowed": True,
								"refundAllowed": True,
								"serviceCodeCheck": False,
								"cardTypeId": "3000",
								"cardTypeName": "MasterCard",
								"characteristic": "C",
								"customFields": {
									"entry": []
								}
							}
						],
						"currencyList": [
							"USD",
							"EUR",
							"GBP",
							"ISK",
							"BYR",
							"ZAR"
						],
						"acquirerInstitutionIdentificationCode": "1"
					}
				]
			}
		]
	}
