#!/usr/bin/env python
# -*- coding: utf8 -*-

from gimpfu import *

from collections import namedtuple

def CreateOptions(name,pairs):
    optsclass=namedtuple(name+'Type',[symbol for symbol,label in pairs]+['labels','labelTuples'])
    opts=optsclass(*(
                    range(len(pairs))
                    +[[label for symbol,label in pairs]]
                    +[[(label,i) for i,(symbol,label) in enumerate(pairs)]]
                    ))
    return opts

Effects=CreateOptions('Effects',[('AMARO','Amaro'),('APOLLO','Apollo'),('BRANNAN','Brannan'),('EARLYBIRD','Earlybird'),('GOTHAM','Gotham'),('INKWELL','Inkwell'),('LORDKELVIN','Lord Kelvin'),('POPROCKET','Poprocket'),('RISE','Rise'),('TOASTER', 'Toaster'),('VALENCIA','Valencia'),('WALDEN','Walden')])

Layers=CreateOptions('Layers',[('LAYER1','Layer 1'),('LAYER2','Layer 2'),('LAYER3','Layer 3'),('VIGNETTE','Vignette'),('COLOR','Color'),('NOISE','Noise'),('BW','Black and White'),('GRADIENT','Gradient'),('MASK','Mask')])

Vignettes=CreateOptions('Vignettes',[('STANDARD','Fits inside the image'),('LARGE','Extends outside the image'),('OBLATE','Flattened'),('NONE','Defaults to an empty layer')])

#adds a new layer from the drawable in selected mode
def AddLayerFromDrawable(draw, img, lg, name, mode = 28, desat = FALSE, opacity = 100):
	l=pdb.gimp_layer_new_from_drawable(draw, img)
	pdb.gimp_image_insert_layer(img, l, lg, 0)
	pdb.gimp_item_set_name(l, Layers.labels[name])
	pdb.gimp_layer_set_mode(l, mode)
	if desat == TRUE:
		pdb.gimp_desaturate_full(l, 0)
	pdb.gimp_layer_set_opacity(l, opacity)
	
	return l

#creates a vignette layer with an ellipse shape and selects the inverse area
def CreateVignette(img, lg, w, h, type, opacity = 100, mode = 28, r = 0, g = 0, b = 0):
	v = AddLayer(img, lg, w, h, Layers.VIGNETTE, opacity, mode)
	pdb.gimp_image_set_active_layer(img, v)
	
	if type == Vignettes.NONE:
		return v
	else:
		#Select an ellipse shape, invert selection and fill
		SelectEllipse(img, w, h, type)
		pdb.gimp_selection_invert(img)
		AddFill(img, v, r, g, b)
		
		return v

#selects a feathered ellipse shape
def SelectEllipse(img, w, h, type):
	if type == Vignettes.STANDARD:
		pdb.gimp_image_select_ellipse(img, 0, 0, 0, w, h)
	elif type == Vignettes.LARGE:
		delta=0.05*w
		pdb.gimp_image_select_ellipse(img, 0, 0-delta, 0-delta, w+(delta*2), h+(delta*2))
	elif type == Vignettes.OBLATE:
		delta = w/6
		epsilon = 0.05*h
		pdb.gimp_image_select_ellipse(img, 0, 0-delta, 0+epsilon, w+delta*2, h-epsilon*2)
	else:
		return
	
	#standardize the feather amount
	feather = 0.20*max(w,h)	
	pdb.gimp_selection_feather(img, feather)

#adds a layer with solid color fill in selected mode
def AddColorLayer(img, name, lg, w, h, opacity, mode, r, g, b):
	c = AddLayer(img, lg, w, h, name, opacity, mode)
	pdb.gimp_context_set_foreground((r, g, b))
	AddFill(img, c, mode, r, g, b)
	
	return c

#adds a new layer with transparent fill
def AddLayer(img, lg, w, h, name, opacity = 100, mode = 28):
	a = pdb.gimp_layer_new(img, w, h, 1, Layers.labels[name], opacity, mode)
	pdb.gimp_image_insert_layer(img, a, lg, 0)
	
	return a

#adds a layer mask - fill(0) is white, fill(1) is black
def AddMask(layer, fill):
	m = pdb.gimp_layer_create_mask(layer, fill)
	pdb.gimp_layer_add_mask(layer, m)
	
	return m

#adds a fill in specified mode and color
def AddFill(img, layer, mode = 28, r = 0, g = 0, b = 0):
	SetContexts(mode, FALSE, r, g, b)
	pdb.gimp_drawable_edit_fill(layer, 0)
	pdb.gimp_selection_clear(img)

#sets gradient contexts
def SetContexts(mode, reverse = FALSE, r = 0, g = 0, b = 0, opacity = 100, singleColor = TRUE, r2 = 255, g2 = 255, b2 = 255):
	pdb.gimp_context_set_opacity(opacity)
	pdb.gimp_context_set_paint_mode(mode)
	pdb.gimp_context_set_gradient_blend_color_space(1)
	pdb.gimp_context_set_gradient_reverse(reverse)
	pdb.gimp_context_set_foreground((r, g, b))
	pdb.gimp_context_set_background((r2, b2, g2))
	if singleColor == TRUE:
		pdb.gimp_context_set_gradient_fg_transparent()
	else:
		pdb.gimp_context_set_gradient_fg_bg_rgb()

def Instagram(img, draw, effect):
	img.disable_undo()
	pdb.gimp_context_push()
	current_f=pdb.gimp_context_get_foreground()
	current_b=pdb.gimp_context_get_background()
	
	#create group
	eName = Effects.labels[effect]
	groupName = eName + " Group"
	lg=pdb.gimp_layer_group_new(img)
	pdb.gimp_image_insert_layer(img, lg, None, 0)
	pdb.gimp_item_set_name(lg, groupName)
	
	#create a layer that acts as the base image for effects
	layer1 = AddLayerFromDrawable(draw, img, lg, Layers.LAYER1)
	
	#calculate image dimensions and some common coordinates
	pdb.gimp_selection_all
	sel_size=pdb.gimp_selection_bounds(img)
	w=sel_size[3]-sel_size[1]
	h=sel_size[4]-sel_size[2]
	
	originX = 0
	originY = 0
	centerX = w/2
	centerY = h/2
	insideX = 0.95*w
	outsideX = 1.50*w
	edgeX = w
	
	if effect == Effects.AMARO:
		
		#adjust curves colors then create vignette
		pdb.gimp_curves_spline(layer1, 1, 8, (0,30, 156,196, 205,203, 255,255))
		pdb.gimp_curves_spline(layer1, 2, 10, (0,0, 61,67, 139,184, 200,206, 255,255))
		pdb.gimp_curves_spline(layer1, 3, 8, (0,20, 146,184, 220,222, 255,255))
		CreateVignette(img, lg, w, h, Vignettes.STANDARD, 60)
	
	elif effect == Effects.APOLLO:
		
		#copy image black and white then add vignette and green layer
		AddLayerFromDrawable(draw, img, lg, Layers.BW, 28, TRUE, 50)
		CreateVignette(img, lg, w, h, Vignettes.LARGE, 40)
		AddColorLayer(img, Layers.COLOR, lg, w, h, 50, 23, 62, 205, 42)
				
	elif effect == Effects.BRANNAN:
		
		#copy image set to overlay and desaturate then adjust hue/saturation
		layer2 = AddLayerFromDrawable(draw, img, lg, Layers.LAYER2, 23, True, 37)
		pdb.gimp_hue_saturation(layer1, 0, 0, 0, -30)
		
		#select second layer copy and merge down
		ml=pdb.gimp_image_merge_down(img, layer2, 1)
		pdb.gimp_item_set_name(ml, Layers.labels[Layers.LAYER1])
		
		#adjust levels colors and brightness/contrast in the merged layer
		pdb.gimp_levels(ml, 0, 0, 255, 1.0, 9, 255)
		pdb.gimp_levels(ml, 1, 0, 228, 1.0, 23, 255)
		pdb.gimp_levels(ml, 2, 0, 255, 1.0, 3, 255)
		pdb.gimp_levels(ml, 3, 0, 239, 1.0, 12, 255)
		Pdb.gimp_brightness_contrast(ml, -8, 25)
		
		#adjust levels colors and brightness/contrast (again)
		pdb.gimp_levels(ml, 0, 0, 255, 0.91, 7, 255)
		pdb.gimp_levels(ml, 1, 0, 255, 1.0, 9, 255)
		pdb.gimp_levels(ml, 2, 0, 224, 1.0, 3, 255)
		pdb.gimp_levels(ml, 3, 0, 255, 0.94, 18, 255)
		pdb.gimp_brightness_contrast(ml, -4, -15)
		
		#add new color layer in multiply mode
		AddColorLayer(img, Layers.COLOR, lg, w, h, 100, 30, 255, 248, 242)
		
	elif effect == Effects.EARLYBIRD:
		
		#adjust hue, saturation, lightness, colors and brightness/contrast
		pdb.gimp_hue_saturation(layer1, 0, 0, 1, -30)
		pdb.gimp_levels(layer1, 0, 0, 255, 1.2, 0, 255)
		pdb.gimp_levels(layer1, 1, 0, 255, 1.0, 25, 255)
		pdb.gimp_brightness_contrast(layer1, 8, 20)
		
		#adjust hue, saturation and lightness (again)
		pdb.gimp_hue_saturation(layer1, 0, 0, 0, -15)
		pdb.gimp_levels(layer1, 0, 0, 235, 0.9, 0, 255)
			
		#add new color layer in multiply mode then add color vignette in normal mode
		AddColorLayer(img, Layers.COLOR, lg, w, h, 100, 30, 252, 243, 214)
		CreateVignette(img, lg, w, h, Vignettes.STANDARD, 60, 28, 184, 184, 184)
			
	elif effect == Effects.GOTHAM:
		
		#desaturate base image
		pdb.gimp_desaturate_full(layer1, 0)
		
		#copy image in hard light mode and adjust color curves
		layer2 = AddLayerFromDrawable(draw, img, lg, Layers.LAYER2, 44)
		pdb.gimp_curves_spline(layer2, 3, 10, (0,0, 63,98, 128,128, 189,159, 255,255))
		
		#add new layer in screen mode then add blur and noise
		layer3 = AddLayerFromDrawable(draw, img, lg, Layers.LAYER3, 31, False, 30)
		pdb.plug_in_mblur(img, layer3, 0, 256, 0, 0, 0)
		pdb.plug_in_rgb_noise(img, layer3, 0, 1, 0.10, 0.10, 0.10, 0)
	
	elif effect == Effects.INKWELL:
		
		#desaturate, adjust color curves and brightness/contrast
		pdb.gimp_desaturate_full(layer1, 0)
		pdb.gimp_curves_spline(layer1, 0, 10, (0,0, 13,0, 83,125, 178,219, 255,255))
		pdb.gimp_brightness_contrast(layer1, -15, 15)
	
	elif effect == Effects.LORDKELVIN:
		
		#adjust color curves
		pdb.gimp_curves_spline(layer1, 0, 4, (10, 0, 255, 255))
		pdb.gimp_curves_spline(layer1, 1, 6, (0,63, 100,200, 255,255))
		pdb.gimp_curves_spline(layer1, 2, 6, (0,30, 180,190, 255,210))
		pdb.gimp_curves_spline(layer1, 3, 6, (0,90, 177,114, 255,188))
	
	elif effect == Effects.POPROCKET:
		
		#add color1 in screen mode and set color gradient
		color1 = CreateVignette(img, lg, w, h, Vignettes.NONE, 100, 31)
		SetContexts(28, FALSE, 206, 39, 70)
		pdb.gimp_drawable_edit_gradient_fill(color1, 2, 0, FALSE, 1, 0, TRUE, centerX, centerY, insideX, centerY)
				
		#add color2 in overlay mode and set color gradient
		color2 = CreateVignette(img, lg, w, h, Vignettes.NONE, 100, 45)
		SetContexts(23, TRUE, 15, 5, 46)
		pdb.gimp_drawable_edit_gradient_fill(color2, 2, 0, FALSE, 1, 0, TRUE, centerX, centerY, outsideX, centerY)
	
	elif effect == Effects.RISE:
		
		#adjust hue saturation and levels
		pdb.gimp_hue_saturation(layer1, 0, 20, 0, -50)
		pdb.gimp_levels(layer1, 0, 0, 255, 1.23, 0, 255)
		
		#add vignette layer in overlay mode
		vignette = CreateVignette(img, lg, w, h, Vignettes.OBLATE, 100, 23)
		
		#set color gradient
		SetContexts(23)
		pdb.gimp_drawable_edit_gradient_fill(vignette, 2, 0, FALSE, 1, 0, TRUE, centerX, centerY, outsideX, centerY)
		pdb.gimp_selection_clear(img)
		
		#add new noise layer in screen mode with opacity 20
		noise = AddColorLayer(img, Layers.NOISE, lg, w, h, 20, 31, 0, 0, 0)
		pdb.plug_in_rgb_noise(img, noise, 0, 0, 0.50, 0.50, 0.50, 0)
			
		#add new color layer in overlay mode
		AddColorLayer(img, Layers.COLOR, lg, w, h, 50, 23, 237, 138, 0)
	
	elif effect == Effects.TOASTER:
		
		#add new layer and adjust color curves
		layer2 = AddLayerFromDrawable(draw, img, lg, Layers.LAYER2)
		pdb.gimp_curves_spline(layer2, 0, 4, (25,0, 255,255))
		
		#add white mask to layer and create black filled ellipse
		layer2Mask = AddMask(layer2, 0)
		SelectEllipse(img, w, h, Vignettes.STANDARD)
		AddFill(img, layer2Mask)
		
		#gradient layer in normal mode, with fg and bg colors set
		gradient = AddLayerFromDrawable(draw, img, lg, Layers.GRADIENT, 28, False, 70)
		SetContexts(28, FALSE, 58, 10, 89, 70, FALSE, 254, 169, 87)
		pdb.gimp_drawable_edit_gradient_fill(gradient, 1, 0, FALSE, 1, 0, TRUE, originX, centerY, edgeX, centerY)
		
		#add new color layer in screen mode
		layer3 = AddColorLayer(img, Layers.LAYER3, lg, w, h, 50, 31, 29, 29, 29)
		
		#add black mask to layer and create white filled ellipse
		layer3Mask = AddMask(layer3, 1)
		SelectEllipse(img, w, h, Vignettes.LARGE)	
		AddFill(img, layer3Mask, 28, 255, 255, 255)
		
		#color layer in dodge mode with mask
		color1 = AddColorLayer(img, Layers.COLOR, lg, w, h, 5, 42, 210, 153, 1)
		
		#add black mask to layer and create white filled ellipse
		color1Mask = AddMask(color1, 1)
		SelectEllipse(img, w, h, Vignettes.LARGE)
		AddFill(img, color1Mask, 28, 255, 255, 255)
			
	elif effect == Effects.VALENCIA:
		
		#add new layer in multiply mode
		color1 = AddColorLayer(img, Layers.COLOR, lg, w, h, 100, 30, 246, 221, 173)
		
		#merge down then adjust color curves and levels
		m=pdb.gimp_image_merge_down(img, color1, 1)
		pdb.gimp_curves_spline(m, 0, 8, (0,50, 75,110, 175,220, 255,255))
		pdb.gimp_levels(m, 3, 0, 255, 1.0, 126, 255)
	
	elif effect == Effects.WALDEN:
		
		#adjust color curves
		pdb.gimp_curves_spline(layer1, 0, 4, (12,0, 255,255))
		pdb.gimp_curves_spline(layer1, 1, 4, (10,0, 247,255))
		pdb.gimp_curves_spline(layer1, 3, 4, (0,38, 255,203))
		
		#adjust levels and color curves (again)
		pdb.gimp_levels(layer1, 0, 0, 235, 1.17, 55, 255)
		pdb.gimp_curves_spline(layer1, 0, 6, (41,0, 125,124, 255,255))
		
		#Create new layer in soft light mode
		gradient = AddLayer(img, lg, w, h, Layers.GRADIENT, 80, 45)
		
		#set contexts and apply gradient in soft light mode starting from top left
		SetContexts(45, FALSE, 255, 255, 255)
		pdb.gimp_drawable_edit_gradient_fill(gradient, 2, 0, FALSE, 1, 0, TRUE, originX, originY, centerX, centerY)
		
	#Clean up
	pdb.gimp_selection_clear(img)
	pdb.gimp_displays_flush()
	pdb.gimp_context_pop()
	img.enable_undo()
	pdb.gimp_context_set_foreground(current_f)
	pdb.gimp_context_set_background(current_b)

register( "gimp_instagram",
  "Add Instagram effects",
  "Add Instagram effects",
  "Simon Bland",
  "Simon Bland based on original work by Marco Crippa 2013",
  "2023-02-03",
  "<Image>/Filters/Instagram",
  'RGB*',
  [(PF_OPTION, 'effect', 'Effect scheme', Effects.AMARO, Effects.labels)],
  '',
  Instagram)

main()

