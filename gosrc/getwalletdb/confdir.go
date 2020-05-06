package main

import (
	"fmt"
	"path/filepath"

	"github.com/configdir-master/configdir"
)

func getFolder() *configdir.Config {
	configDirs := configdir.New("Pktwallet", "pkt")
	configDirs.LocalPath, _ = filepath.Abs(".")
	folder := configDirs.QueryFolderContainsFile("wallet.db")
	return folder
}

func main() {
	foldr := getFolder()

	if foldr == nil {
		fmt.Println("Path not found")
	} else {
		fmt.Println(foldr.Path)
	}

}
