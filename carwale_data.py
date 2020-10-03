import scrapy
import json
#https://www.carwale.com/porsche-cars/macan/

class PostSpider(scrapy.Spider):
    name = "carzz"
    # companies URL
    start_urls = [
        # "https://www.carwale.com/marutisuzuki-cars/",
        # "https://www.carwale.com/hyundai-cars/",
        # "https://www.carwale.com/mahindra-cars/",
        # "https://www.carwale.com/tata-cars/",
        # "https://www.carwale.com/toyota-cars/",
        # "https://www.carwale.com/renault-cars/",
        # "https://www.carwale.com/honda-cars/",
        # "https://www.carwale.com/mg-cars/",
        # "https://www.carwale.com/ford-cars/",
        # "https://www.carwale.com/kia-cars/",
        # "https://www.carwale.com/volkswagen-cars/",
        # "https://www.carwale.com/mercedesbenz-cars/",
        # 'https://www.carwale.com/bmw-cars/',
        #  'https://www.carwale.com/skoda-cars/',
        #  'https://www.carwale.com/audi-cars/',
        #  'https://www.carwale.com/jeep-cars/',
        #  'https://www.carwale.com/datsun-cars/',
        #  'https://www.carwale.com/landrover-cars/',
        #  'https://www.carwale.com/nissan-cars/',
        #  'https://www.carwale.com/jaguar-cars/',
        #  'https://www.carwale.com/volvo-cars/',
         'https://www.carwale.com/porsche-cars/'
         # 'https://www.carwale.com/lexus-cars/',
         # 'https://www.carwale.com/fiat-cars/',
         # 'https://www.carwale.com/lamborghini-cars/',
         # 'https://www.carwale.com/isuzu-cars/',
         # 'https://www.carwale.com/mitsubishi-cars/',
         # 'https://www.carwale.com/mini-cars/',
         # 'https://www.carwale.com/forcemotors-cars/',
         # 'https://www.carwale.com/bentley-cars/',
         # 'https://www.carwale.com/rollsroyce-cars/',
         # 'https://www.carwale.com/ferrari-cars/',
         # 'https://www.carwale.com/maserati-cars/',
         # 'https://www.carwale.com/astonmartin-cars/',
         # 'https://www.carwale.com/bugatti-cars/',
         # 'https://www.carwale.com/tesla-cars/',
         # 'https://www.carwale.com/citroen-cars/',
         # 'https://www.carwale.com/haval-cars/'
    ]

    # this will find all available model for given company
    # EX: for Maruti Suzuki(https://www.carwale.com/marutisuzuki-cars/) - swift, alto, ertiga ,...
    def parse(self, response):
        div_ul = response.css(".o-dpDliG ")
        ul_list = div_ul[0].css("ul")
        list_cars = ul_list[0].css("li")

        for i in list_cars:
            url_car_model = "https://www.carwale.com" + i.css("a.o-brXWGL::attr(href)").get()
            yield scrapy.Request(url_car_model, callback = self.parse_dir_contents)


    # this will find all available variants for perticular cars
    # EX for Swift(https://www.carwale.com/marutisuzuki-cars/swift/): Swift LXI, Swift VxI, Swift ZxI, ...
    def parse_dir_contents(self, response):
        for i in response.css("table"):
            if "_3FHoSi" in i.get():
                main_table = i
                break

        for i in main_table.css("h3 ::attr(href)").getall():
            url = "https://www.carwale.com" + i
            yield scrapy.Request(url, callback = self.parse_car_contents)

    # this will find all specification and features of given car model and store it in json format
    # EX: https://www.carwale.com/marutisuzuki-cars/swift/lxi/ -- it will find all Specifications & Features
    def parse_car_contents(self, response):
        all_details_dct = {"car_name": response.css("h1::text").get(),
                            "car_version": response.css(".o-cRSqer ::text")[1].get(),
                            "summary":  " ".join(response.css("._3nFEly ::text").getall()),
                            "specifications":[],
                            "cities_on_road_prices":[]}

        lst = response.css(".o-fHmpzP ::text").getall()

        start_index = []
        for i in lst:
            if "Engine" == i:
                start_index.append(lst.index(i))
            elif "Warranty (Kilometres)" in i:
                end_index = lst.index(i) + 2
            elif "Engine Type" == i:
                start_index.append(lst.index(i))

        start_index = sorted(start_index)[0]

        # Every car details ends with Warranty (Years) but there are some exceptions
        try:
            try:
                print(end_index)
            except NameError:
                end_index = lst.index("Voice Command") + 2
        except:
            end_index = lst.index("Warranty (Years)") + 2

        try:
            if lst[start_index] == "Get Offers from Dealer":
                start_index += 1
        except:
            pass

        all_details = lst[start_index:end_index]

        for i in all_details:
            if "View all" in i:
                all_details.remove(i)
            else:
                continue


        keys = all_details[::2]
        val = all_details[1::2]
        if len(keys) == len(val):
            for i in range(len(keys)):
                all_details_dct["specifications"].append({"field": keys[i], "value": val[i]})

        # #find prices in all cities
        x = response.css("section.o-fzptVd")
        for i in x:
            if i.css("header.o-fznJDS ") and i.css("div.o-fznJDS "):
                z = i
                try:
                    if "City" in z.css("thead").css("tr").get():
                        final_table = i
                        break
                    else:
                        continue
                except TypeError:
                    continue
            else:
                continue
        try:
            lst_details = final_table.css("tbody._3-jMlO ::text").getall()
            key = lst_details[::2]
            val = lst_details[1::2]

            if len(key) == len(val):
                for i in range(len(key)):
                    all_details_dct["cities_on_road_prices"].append({"city":key[i], "price":val[i]})
        except NameError:
            all_details_dct["cities_on_road_prices"].append({"city":"", "price":""})


        # name = "_".join(response.css('h1::text').get().split())
        # with open(f"carwale\\other_cars\\porsche_cars\\{name}.json", "w") as outfile:
        #     json.dump(all_details_dct, outfile)

        yield all_details_dct
