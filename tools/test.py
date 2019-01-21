from homebrew import *

wort = Wort()

wort.add_water(3)
wort.add_malt([MaltAddition(1.035, 3.3), # CBW Goldpils Vienna
			   MaltAddition(1.035, 3.3), # CBW Pale ale
			   MaltAddition(1.036, 3.3), # Maillards Gold
			   MaltAddition(1.025, 2) # Malt grains
			   ])
wort.add_hops([HopAddition(6, 1, 60), # UK East Kent Golding
			   HopAddition(4.2, 1, 30), # Willamette
			   HopAddition(12.6, 1, 60), # Nugget
			   HopAddition(10.1, 2, 60) # Mosaic
			   ])
wort.add_water(2)

print(wort.calculate_ibu())
print(wort.calculate_gravity())

beer = wort.ferment(OG = 1.072)
print(beer.calculate_abv())
