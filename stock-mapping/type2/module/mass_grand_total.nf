/** total stock
-----------------------------------------------------------------------**/

include { multijoin } from './defs.nf'

workflow mass_grand_total {

    take:
    street; rail; other; building


    main:
    mass_grand_total_t_10m2(
        multijoin(
           [street, 
            rail, 
            other, 
            building], [0,1]
        )
    ) \
    | mass_grand_total_t_10m2_nodata_remove \
    | mass_grand_total_kt_100m2 \
    | mass_grand_total_Mt_1km2 \
    | mass_grand_total_Gt_10km2

}


process mass_grand_total_t_10m2 {

    label 'mem_4'

    input:
    tuple val(tile), val(state), 
        file(street), file(rail), file(other), file(building)

    output:
    tuple val(tile), val(state), file('mass_grand_total_t_10m2.tif')

    publishDir "$params.dir.pub/$state/$tile", mode: 'copy'

    """
    gdal_calc.py \
        -A $street \
        -B $other \
        -C $rail \
        -D $building \
        --calc="(A+B+C+D)" \
        --outfile=mass_grand_total_t_10m2.tif \
        $params.gdal.calc_opt_float
    """

}


process mass_grand_total_t_10m2_nodata_remove {

    input:
    tuple val(tile), val(state), file(mass)

    output:
    tuple val(tile), val(state), file('mass_grand_total_t_10m2_nodata_remove.tif')

    """
    cp $mass temp.tif
    gdal_edit.py -a_nodata 32767 temp.tif
    gdal_calc.py \
        -A temp.tif \
        --calc="(A*(A>0))" \
        --outfile=mass_grand_total_t_10m2_nodata_remove.tif \
        $params.gdal.calc_opt_float
    """

}


process mass_grand_total_kt_100m2 {

    input:
    tuple val(tile), val(state), file(mass)

    output:
    tuple val(tile), val(state), file('mass_grand_total_kt_100m2.tif')

    publishDir "$params.dir.pub/$state/$tile", mode: 'copy'

    """
    gdal_translate \
        -tr 100 100 -r average \
        $params.gdal.tran_opt_float \
        $mass temp.tif
    # t/m² -> kt/100m²
    gdal_calc.py \
        -A temp.tif \
        --calc="(A*10*10/1000)" \
        --outfile=mass_grand_total_kt_100m2.tif \
        $params.gdal.calc_opt_float
    """

}


process mass_grand_total_Mt_1km2 {

    input:
    tuple val(tile), val(state), file(mass)

    output:
    tuple val(tile), val(state), file('mass_grand_total_Mt_1km2.tif')

    publishDir "$params.dir.pub/$state/$tile", mode: 'copy'

    """
    gdal_translate \
        -tr 1000 1000 -r average \
        $params.gdal.tran_opt_float \
        $mass temp.tif
    # kt/100m² -> Mt/km²
    gdal_calc.py \
        -A temp.tif \
        --calc="(A*10*10/1000)" \
        --outfile=mass_grand_total_Mt_1km2.tif \
        $params.gdal.calc_opt_float
    """

}


process mass_grand_total_Gt_10km2 {

    input:
    tuple val(tile), val(state), file(mass)

    output:
    tuple val(tile), val(state), file('mass_grand_total_Gt_10km2.tif')

    publishDir "$params.dir.pub/$state/$tile", mode: 'copy'

    """
    gdal_translate \
        -tr 10000 10000 -r average \
        $params.gdal.tran_opt_float \
        $mass temp.tif
    # Mt/km² -> Gt/10km²
    gdal_calc.py \
        -A temp.tif \
        --calc="(A*10*10/1000)" \
        --outfile=mass_grand_total_Gt_10km2.tif \
        $params.gdal.calc_opt_float
    """

}

